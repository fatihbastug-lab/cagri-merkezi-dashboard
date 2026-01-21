import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Genişliği ve Başlık
st.set_page_config(layout="wide", page_title="Kalite & MMA Entegre Analiz")

st.title("📞 Çağrı Merkezi Performans Dashboard (Kalite & MMA)")
st.markdown("---")

# --- YAN PANEL: DOSYA YÜKLEME ---
st.sidebar.header("📁 Veri Kaynakları")
kalite_file = st.sidebar.file_uploader("1. Kalite Detay Liste CSV Yükle", type="csv")
mma_file = st.sidebar.file_uploader("2. MMA Ham Data CSV Yükle", type="csv")

if kalite_file and mma_file:
    # Verileri Oku
    df_kalite = pd.read_csv(kalite_file)
    df_mma = pd.read_csv(mma_file)

    # Ortak anahtar üzerinden birleştirme (Sicil = Agent ID)
    # Not: DetayListe'de 'Sicil', MMA'da 'Agent ID' sütunlarını kullanıyoruz
    df_mma['Agent ID'] = df_mma['Agent ID'].astype(str)
    df_kalite['Sicil'] = df_kalite['Sicil'].astype(str)
    
    # Personel bazlı özet tablolar hazırlama
    kalite_ozet = df_kalite.groupby('Personel').agg({
        'Form Puan': 'mean',
        'Sicil': 'first',
        'Takım Adı': 'first'
    }).reset_index()

    mma_ozet = df_mma.groupby('Agent ID').agg({
        'Soru Puan 1': 'mean',
        'Soru Puan 2': 'mean',
        'Müşteri Temsilcisi Adı': 'count'
    }).rename(columns={'Müşteri Temsilcisi Adı': 'Anket Sayısı'}).reset_index()

    # İki tabloyu birleştir
    master_df = pd.merge(kalite_ozet, mma_ozet, left_on='Sicil', right_on='Agent ID', how='inner')

    # --- ÜST KPI KARTLARI ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Genel Kalite Ort.", f"{df_kalite['Form Puan'].mean():.1f}")
    kpi2.metric("Genel MMA Puanı", f"{df_mma['Soru Puan 1'].mean():.1f}")
    kpi3.metric("Toplam Dinleme", len(df_kalite))
    kpi4.metric("Toplam Anket", len(df_mma))

    st.markdown("---")

    # --- GRAFİKLER ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🎯 Kalite vs MMA Korelasyonu")
        # Kalite puanı ile müşteri memnuniyeti arasındaki ilişki
        fig_corr = px.scatter(master_df, x="Form Puan", y="Soru Puan 1", 
                             hover_name="Personel", size="Anket Sayısı",
                             color="Takım Adı", title="Puan Karşılaştırması")
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_right:
        st.subheader("📉 En Çok Puan Kaybedilen Kriterler")
        # Detay listedeki 0/100 puanlı sütunların ortalamasını alıyoruz
        kriter_listesi = ['Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları', 
                          'Bekletme', 'Etkin Dinleme- Çözüm Odaklı Yaklaşım', 
                          'Görüşme Hâkimiyeti- Sahiplenme', 'Doğru Bilgilendirme']
        
        # Mevcut sütunları kontrol et ve ortalama al
        mevcut_kriterler = [c for c in kriter_listesi if c in df_kalite.columns]
        if mevcut_kriterler:
            kriter_puanlari = df_kalite[mevcut_kriterler].mean().sort_values().reset_index()
            kriter_puanlari.columns = ['Kriter', 'Başarı Oranı']
            fig_bar = px.bar(kriter_puanlari, x='Başarı Oranı', y='Kriter', orientation='h', color='Başarı Oranı')
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- RİSKLİ DURUMLAR VE ANALİZ ---
    st.markdown("---")
    st.subheader("⚠️ Kritik Analiz Tablosu")
    
    tab1, tab2 = st.tabs(["Düşük Performanslılar", "MMA Detay Notları"])
    
    with tab1:
        # Hem kalite hem MMA puanı 70'in altında olanlar
        riskli_mt = master_df[(master_df['Form Puan'] < 75) | (master_df['Soru Puan 1'] < 3)]
        st.dataframe(riskli_mt[['Personel', 'Takım Adı', 'Form Puan', 'Soru Puan 1', 'Anket Sayısı']], use_container_width=True)

    with tab2:
        # MMA dosyasındaki ham açıklamalar
        st.dataframe(df_mma[['Müşteri Temsilcisi Adı', 'Çağrı Konusu', 'Açıklama', 'Anket Tarihi']].tail(20), use_container_width=True)

else:
    st.warning("Lütfen sol taraftaki panelden her iki CSV dosyasını (Kalite ve MMA) yükleyin.")
    st.info("İpucu: 'DetayListe' ve 'MMA Tespit Aksiyon Data' dosyalarını kullanmalısınız.")
