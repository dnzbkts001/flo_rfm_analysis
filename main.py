import os
import pandas as pd
from src.data_preparation import load_and_copy_data, check_dataframe, process_and_create_features, check_channel_distributions, top_profitable_customers, top_frequent_customers, create_rfm_dataframe

# Yeni modülümüzü import ediyoruz
from src.rfm_analysis import calculate_rfm_metrics, calculate_rfm_scores_and_segments, export_target_segments

def configure_pandas():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)


def main():
    configure_pandas()
    csv_path = os.path.join("data", "flo_data_20k.csv")

    print("🚀 FLO RFM Analiz Projesi Çalıştırılıyor...\n")

    # Görev 1: Veri Ön Hazırlık Süreci
    df_prepared = create_rfm_dataframe(csv_path)

    # Görev 2: RFM Metriklerinin Hesaplanması
    rfm_df = calculate_rfm_metrics(df_prepared)

    # =========================================================================
    # GÖREV 3: RFM Skorlarının Hesaplanması ve Segmentasyonu
    # =========================================================================
    rfm_final = calculate_rfm_scores_and_segments(rfm_df)

    # Segmentlerin Örnek Gözlemi
    # print("\n==================== RFM SEGMENTS SAMPLES ====================")
    # print(rfm_final[["master_id", "RFM_SCORE", "segment"]].sort_values(by="master_id").head(10))

    # Segmentlerin Dağılım Analizi (Hangi segmentte kaç müşteri var ve ortalamaları neler?)
    # print("\n==================== SEGMENT DISTRIBUTIONS SUMMARY ====================")
    # segment_summary = rfm_final.groupby("segment").agg({
    #     "master_id": "count",
    #     "recency": "mean",
    #     "frequency": "mean",
    #     "monetary": "mean"
    # })
    # segment_summary.columns = ["Count", "Mean_Recency", "Mean_Frequency", "Mean_Monetary"]
    # print(segment_summary.sort_values(by="Count", ascending=False))

    # =========================================================================
    # GÖREV 4: Aksiyon Zamanı (İş Problemlerinin Çözümü)
    # =========================================================================
    export_target_segments(rfm_final, df_prepared)


if __name__ == "__main__":
    main()