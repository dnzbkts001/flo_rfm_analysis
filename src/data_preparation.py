import pandas as pd
import numpy as np


def load_and_copy_data(file_path: str) -> pd.DataFrame:
    """
    Veri setini okur ve orijinal veriyi korumak adına bir kopyasını döner.
    """
    df = pd.read_csv(file_path)
    return df.copy()


def check_dataframe(dataframe: pd.DataFrame, head_count: int = 10) -> bool:
    """
    Veri setinin genel yapısını inceler ve veri bütünlüğünü doğrular.

    Returns:
        bool: Eğer veri bütünlüğü tamsa (mükerrer yoksa) True, mükerrer varsa False döner.
    """
    print("==================== FIRST 10 ROWS ====================")
    print(dataframe.head(head_count))

    print("\n==================== COLUMN NAMES ====================")
    print(dataframe.columns.tolist())

    print("\n==================== DESCRIPTIVE STATISTICS ====================")
    print(dataframe.describe(include=[np.number], percentiles=[0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T)


    print("\n==================== DATA INTEGRITY (UNIQUENESS) ====================")
    total_rows = len(dataframe)
    unique_ids = dataframe["master_id"].nunique()
    print(f"Total Number of Observations (Rows) : {total_rows}")
    print(f"Number of Unique Customer IDs       : {unique_ids}")

    is_integrated = total_rows == unique_ids

    if is_integrated:
        print("SUCCESS: All master_id values are unique. Data integrity is verified.")
    else:
        print("WARNING: Duplicate master_id values detected! Dynamic aggregation will be applied.")

    print("\n==================== DATA TYPES & INFOS ====================")
    print(dataframe.info())

    return is_integrated


def process_and_create_features(dataframe: pd.DataFrame, apply_aggregation: bool = False) -> pd.DataFrame:
    """
    Veri bütünlüğü durumuna göre veriyi işler ve omnichannel değişkenlerini türetir.

    Args:
        dataframe (pd.DataFrame): İşlem yapılacak veri seti.
        apply_aggregation (bool): Mükerrer kayıt uyarısı alındıysa True geçilerek GroupBy çalıştırılır.
    """
    if apply_aggregation:
        print("Mükerrer kayıtlar saptandığı için GroupBy agregasyonu başlatılıyor...")
        dataframe = dataframe.groupby("master_id").agg({
            "order_num_total_ever_online": "sum",
            "order_num_total_ever_offline": "sum",
            "customer_value_total_ever_online": "sum",
            "customer_value_total_ever_offline": "sum",
        }).reset_index()
    else:
        print("Veri bütünlüğü tam. Doğrudan değişken türetme adımına geçiliyor...")

    # Omnichannel değişkenlerinin oluşturulması
    dataframe["total_order_num"] = (
            dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    )
    dataframe["total_customer_value"] = (
            dataframe["customer_value_total_ever_online"] + dataframe["customer_value_total_ever_offline"]
    )

    # Tarih Değişkenlerinin Tip Dönüşümü
    date_columns = [col for col in dataframe.columns if "date" in col]

    print("date_columns : ", date_columns)

    for col in date_columns:
        dataframe[col] = pd.to_datetime(dataframe[col])



    return dataframe


def check_channel_distributions(dataframe: pd.DataFrame) -> None:
    """
    Alışveriş kanallarındaki müşteri sayısını, toplam ürün adedini ve
    toplam harcama dağılımlarını hesaplar ve ekrana yazdırır.

    Args:
        dataframe (pd.DataFrame): Analiz edilecek veri seti.
    """
    print("\n==================== CHANNEL DISTRIBUTIONS ====================")

    channel_analysis = dataframe.groupby("order_channel").agg({
        "master_id": "count",  # Kanal bazlı müşteri sayısı
        "total_order_num": ["sum", "mean"],  # Toplam ve ortalama sipariş adedi
        "total_customer_value": ["sum", "mean"]  # Toplam ve ortalama bırakılan ciro
    })

    # Sütun isimlerini daha okunabilir ve profesyonel hale getirelim
    channel_analysis.columns = [
        "Customer_Count",
        "Total_Order_Sum", "Average_Order_Per_Customer",
        "Total_Value_Sum", "Average_Value_Per_Customer"
    ]

    # Müşteri sayısına göre çoktan aza sıralayalım
    channel_analysis = channel_analysis.sort_values(by="Customer_Count", ascending=False)

    print(channel_analysis)


def top_profitable_customers(dataframe: pd.DataFrame, top_n: int = 10) -> None:
    """
    Şirkete en fazla kazanç getiren ilk N müşteriyi sıralar ve ekrana yazdırır.

    Args:
        dataframe (pd.DataFrame): İşlem yapılacak veri seti.
        top_n (int): Listelenecek müşteri sayısı.
    """
    print(f"\n==================== TOP {top_n} MOST PROFITABLE CUSTOMERS ====================")

    top_customers = dataframe[["master_id", "total_customer_value", "total_order_num"]].sort_values(
        by="total_customer_value",
        ascending=False
    ).head(top_n)

    # Okunabilirliği arttırmak için indeksi 1'den başlatalım
    top_customers.index = range(1, top_n + 1)
    print(top_customers)


def top_frequent_customers(dataframe: pd.DataFrame, top_n: int = 10) -> None:
    """
    Şirketten en fazla sipariş veren (en sık alışveriş yapan) ilk N müşteriyi
    sıralar ve ekrana yazdırır.

    Args:
        dataframe (pd.DataFrame): İşlem yapılacak veri seti.
        top_n (int): Listelenecek müşteri sayısı.
    """
    print(f"\n==================== TOP {top_n} MOST FREQUENT CUSTOMERS ====================")

    top_customers = dataframe[["master_id", "total_order_num", "total_customer_value"]].sort_values(
        by="total_order_num",
        ascending=False
    ).head(top_n)

    # Profesyonel bir görünüm için indeksi 1'den başlatalım
    top_customers.index = range(1, top_n + 1)
    print(top_customers)


# ADIM 8: TÜM ÖN HAZIRLIK SÜRECİNİ YÖNETEN ANA FONKSİYON
def create_rfm_dataframe(file_path: str) -> pd.DataFrame:
    """
    Tüm veri ön hazırlık sürecini (Pipeline) tek bir çatı altında toplar.
    Veriyi okur, bütünlüğü inceler, gerekirse tekilleştirir, tarihleri dönüştürür
    ve yeni omnichannel değişkenlerini türeterek temiz DataFrame'i döner.
    """
    print("[PIPELINE] Veri ön hazırlık süreci başlatılıyor...")

    # 1. Veriyi Yükleme
    df = load_and_copy_data(file_path)

    # 2. Veri Bütünlüğü Kontrolü (Mükerrer Analizi)
    total_rows = len(df)
    unique_ids = df["master_id"].nunique()
    apply_aggregation = total_rows != unique_ids

    # 3. Gerekirse Güvenli Agregasyon, Gerekmiyorsa Doğrudan İşleme
    if apply_aggregation:
        df = df.groupby("master_id").agg({
            "order_num_total_ever_online": "sum",
            "order_num_total_ever_offline": "sum",
            "customer_value_total_ever_online": "sum",
            "customer_value_total_ever_offline": "sum",
        }).reset_index()

    # 4. Tarih Değişkenlerinin Dönüştürülmesi
    date_columns = [col for col in df.columns if "date" in col]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])

    # 5. Omnichannel Değişkenlerinin Türetilmesi
    df["total_order_num"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["total_customer_value"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]

    print("[PIPELINE] Veri ön hazırlık süreci başarıyla tamamlandı.")
    return df