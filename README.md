# FLO | RFM Tabanlı Müşteri Segmentasyon Analizi

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Pandas-Data%20Science-orange.svg" alt="Pandas">
  <img src="https://img.shields.io/badge/Analytics-RFM%20Segmentation-brightgreen.svg" alt="RFM">
</p>

## 📌 Proje Genel Bakış
Bu proje, FLO'nun (ayakkabı şirketi) omni-channel (hem online hem offline) satış stratejilerini optimize etmek amacıyla, veri odaklı müşteri segmentasyonu gerçekleştirmek üzere tasarlanmıştır. 20.000 müşterinin geçmiş alışveriş davranışları analiz edilerek **Recency (Yenilik)**, **Frequency (Sıklık)** ve **Monetary (Bırakılan Değer)** metrikleri hesaplanmış, ardından müşteriler küresel pazarlama standartlarında 10 farklı davranışsal segmente ayrılmıştır.

---

## 📂 Proje Mimarisi (Production-Ready)
Proje, monolitik (tek parça) spagetti kod yapısından kaçınılarak, kurumsal standartlarda **modüler ve genişletilebilir** bir mimariyle geliştirilmiştir:

```text
flo_rfm_analysis/
│
├── src/
│   ├── __init__.py
│   ├── data_preparation.py      # Veri yükleme, temizleme ve bütünlük doğrulama
│   └── rfm_analysis.py          # Metrik hesaplama, rank-qcut skorlama ve aksiyon listeleri
│
├── output/                      # Pazarlama departmanına teslim edilen hedef listeler
│   ├── erkek_cocuk_indirim_hedef_kitle.csv
│   └── yeni_kadin_markasi_hedef_kitle.csv
│
├── main.py                      # Projeyi ayağa kaldıran ana boru hattı (Pipeline)
├── requirements.txt             # Proje bağımlılıkları
└── .gitignore                   # Git tarafından takip edilmeyecek güvenli alan tanımları