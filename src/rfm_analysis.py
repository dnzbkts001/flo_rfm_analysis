import pandas as pd
import datetime as dt
import os


def calculate_rfm_metrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Hazırlanmış dataframe üzerinden Recency, Frequency ve Monetary
    metriklerini hesaplar ve yeni bir RFM dataframe'i döner.
    """
    print("\n [RFM] Recency, Frequency ve Monetary metrikleri hesaplanıyor...")

    # 1. Analiz tarihinin belirlenmesi (Veri setindeki son alışveriş tarihinden 2 gün sonrası)
    max_date = dataframe["last_order_date"].max()
    analysis_date = max_date + dt.timedelta(days=2)
    print(f"Veri Setindeki Son Alışveriş Tarihi: {max_date.strftime('%Y-%m-%d')}")
    print(f"Analiz İçin Baz Alınan Bugünün Tarihi: {analysis_date.strftime('%Y-%m-%d')}")

    # 2. RFM Metriklerinin Oluşturulması
    rfm = pd.DataFrame()

    # Müşteri ID'sini taşıyalım
    rfm["master_id"] = dataframe["master_id"]

    # Recency: Analiz tarihi ile müşterinin son alışveriş tarihi arasındaki gün farkı
    rfm["recency"] = (analysis_date - dataframe["last_order_date"]).dt.days

    # Frequency: Toplam sipariş sayısı
    rfm["frequency"] = dataframe["total_order_num"]

    # Monetary: Toplam müşteri değeri (harcaması)
    rfm["monetary"] = dataframe["total_customer_value"]

    print("[RFM] Metrik hesaplama işlemi başarıyla tamamlandı.")
    return rfm


def calculate_rfm_scores_and_segments(rfm_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Metrikleri 1-5 arası skorlara dönüştürür, RFM skorunu türetir
    ve standart segmentasyon eşlemesini yapar.
    """
    print("[RFM] Skorlama ve Segmentasyon süreci başlatılıyor...")

    # 1. Skorların Hesaplanması (rank(method='first') ile çoklayan değerleri güvenle böleriz)
    rfm_dataframe["recency_score"] = pd.qcut(
        rfm_dataframe["recency"], q=5, labels=[5, 4, 3, 2, 1]
    )

    rfm_dataframe["frequency_score"] = pd.qcut(
        rfm_dataframe["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]
    )

    rfm_dataframe["monetary_score"] = pd.qcut(
        rfm_dataframe["monetary"], q=5, labels=[1, 2, 3, 4, 5]
    )

    # 2. RF_SCORE Oluşturulması (Müşteri davranışını analiz ederken Monetary skoru genellikle
    # segmentasyona dahil edilmez, dünyada standart kabul edilen yapı Recency ve Frequency birleşimidir)
    rfm_dataframe["RFM_SCORE"] = (
            rfm_dataframe["recency_score"].astype(str) +
            rfm_dataframe["frequency_score"].astype(str)
    )

    # 3. Segment Tanımlamalarının Yapılması (Regex Map)
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm_dataframe["segment"] = rfm_dataframe["RFM_SCORE"].replace(seg_map, regex=True)

    print("[RFM] Skorlama ve segmentasyon başarıyla tamamlandı.")
    return rfm_dataframe


def export_target_segments(rfm_dataframe: pd.DataFrame, source_dataframe: pd.DataFrame) -> None:
    """
    Pazarlama departmanından gelen 2 farklı iş problemini çözer,
    hedef müşteri listelerini filtreler ve 'output/' klasörüne CSV olarak kaydeder.
    """
    print("\n[AKSİYON] İş problemleri için hedef kitle analizleri başlatılıyor...")

    # Çıktıların kaydedileceği klasörü dinamik olarak oluşturalım
    os.makedirs("output", exist_ok=True)

    # İlgilenilen kategorileri (interested_in_categories_12) rfm dataframe'ine geçici olarak bağlayalım
    # (Merge işlemi yaparken index veya master_id kullanabiliriz)
    merged_df = pd.merge(rfm_dataframe, source_dataframe[["master_id", "interested_in_categories_12"]], on="master_id")

    # -------------------------------------------------------------------------
    # ANALİZ 1: Yeni Kadın Markası Tanıtımı
    # Kriterler: Segmentler -> champions veya loyal_customers, Kategori -> KADIN içermeli
    # -------------------------------------------------------------------------
    target_segments_1 = ["champions", "loyal_customers"]

    target_customers_1 = merged_df[
        (merged_df["segment"].isin(target_segments_1)) &
        (merged_df["interested_in_categories_12"].str.contains("KADIN", na=False))
        ]["master_id"]

    target_customers_1.to_csv("output/yeni_kadin_markasi_hedef_kitle.csv", index=False, header=False)
    print(
        f"Analiz 1 Tamamlandı: {len(target_customers_1)} müşteri 'output/yeni_kadin_markasi_hedef_kitle.csv' dosyasına kaydedildi.")

    # -------------------------------------------------------------------------
    # ANALİZ 2: Erkek ve Çocuk Kategorisinde İndirim
    # Kriterler: Segmentler -> about_to_sleep veya cant_loose, Kategori -> ERKEK veya COCUK içermeli
    # -------------------------------------------------------------------------
    target_segments_2 = ["about_to_sleep", "cant_loose"]

    target_customers_2 = merged_df[
        (merged_df["segment"].isin(target_segments_2)) &
        (
                merged_df["interested_in_categories_12"].str.contains("ERKEK", na=False) |
                merged_df["interested_in_categories_12"].str.contains("COCUK", na=False)
        )
        ]["master_id"]

    target_customers_2.to_csv("output/erkek_cocuk_indirim_hedef_kitle.csv", index=False, header=False)
    print(
        f"Analiz 2 Tamamlandı: {len(target_customers_2)} müşteri 'output/erkek_cocuk_indirim_hedef_kitle.csv' dosyasına kaydedildi.")