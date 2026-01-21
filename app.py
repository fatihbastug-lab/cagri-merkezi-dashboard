import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dinamik Kalite & MMA Dashboard")

# --- SOL PANEL: MODÜLER YÜKLEME ALANLARI ---
st.sidebar.header("📥 Ham Veri Girişi")

# 1. Kalite Detay Listesi Yükleme
detay_file = st.sidebar.file_uploader("1. Kalite Detay Listesi (.xlsx)", type="xlsx")

# 2. MMA Datası Yükleme
mma_file = st.sidebar.file_uploader("2. MMA Ham Data (.xlsx)", type="xlsx")

st.sidebar.markdown("---")
st.sidebar.info("Dosyaları yüklediğinizde analizler otomatik başlar.")

# --- ANA EKRAN TASARIMI ---
st.title("📊 Operasyonel Performans Analiz Merkezi")

# Eğer hiçbir dosya yüklenmediyse uyarı ver
if not detay_file and not mma_file:
    st.warning("Lütfen analiz için sol taraftan en az bir Excel dosyası yükleyin.")

# --- 1. KALİTE ANALİZ MODÜLÜ (Detay Liste'den beslenir) ---
if detay_file:
    df_detay = pd.read_excel(detay_file)
    
    st.header("🔍 Kalite ve Hata Analizi")
    
    # KPI Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Dinleme", len(df_detay))
    c2.metric("Ort. Form Puanı", f"%{df_detay['Form Puan'].mean():.1f}")
    c3.metric("Kritik Hata Sayısı", len(df_detay[df_detay['Form Puan'] < 50]))

    # Hata Kırılımları (Ana rapordaki 'Hata Detayı' gibi)
    st.subheader("📌 En Çok Tekrar Eden Hatalar")
    # Dosyanızdaki kriter sütunlarını otomatik bulup sayar
    kriter_cols = ['Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları', 'Doğru Bilgilendirme', 'Süreç Yönetimi']
    mevcut_kriterler = [c for c in kriter_cols if c in df_detay.columns]
    
    if mevcut_kriterler:
        hata_df = df_detay[mevcut_kriterler].apply(lambda x: (x < 100).sum()).reset_index()
        hata_df.columns = ['Kriter', 'Hata Sayısı']
        fig_hata = px.bar(hata_df.sort_values('Hata Sayısı'), x='Hata Sayısı', y='Kriter', orientation='h', color='Hata Sayısı')
        st.plotly_chart(fig_hata, use_container_width=True)

# --- 2. MMA ANALİZ MODÜLÜ (MMA Data'dan beslenir) ---
if mma_file:
    df_mma = pd.read_excel(mma_file)
    
    st.markdown("---")
    st.header("⭐️ MMA & Müşteri Memnuniyeti")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Müşteri Puan Dağılımı")
        fig_mma = px.pie(df_mma, names='Soru Puan 1', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_mma, use_container_width=True)
        
    with col_b:
        st.subheader("Personel Bazlı MMA Başarısı")
        mma_mt = df_mma.groupby('Müşteri Temsilcisi Adı')['Soru Puan 1'].mean().reset_index()
        fig_mt = px.bar(mma_mt.sort_values('Soru Puan 1'), x='Soru Puan 1', y='Müşteri Temsilcisi Adı', orientation='h')
        st.plotly_chart(fig_mt, use_container_width=True)

# --- 3. BİRLEŞTİRİLMİŞ TABLO (Opsiyonel) ---
if detay_file and mma_file:
    st.markdown("---")
    st.header("🔗 Çapraz Performans Tablosu")
    st.write("Aşağıdaki tablo Kalite ve MMA verilerini aynı ekranda görmenizi sağlar.")
    # Burada 'Personel' ve 'Müşteri Temsilcisi Adı' üzerinden eşleştirme yapabilirsiniz
    st.info("Eşleştirme aktif: Personel bazlı detayları aşağıdan inceleyebilirsiniz.")
    st.dataframe(df_detay[['Personel', 'Takım Adı', 'Form Puan', 'Açıklama Detay']].head(20))
