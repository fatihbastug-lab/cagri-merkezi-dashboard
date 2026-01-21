import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Çağrı Merkezi Analitik", layout="wide")

# Başlık
st.title("🚀 Çağrı Merkezi Kalite & Hata Dashboard")
st.markdown("Verileri yükleyin ve operasyonel performansı anlık izleyin.")

# 1. DOSYA YÜKLEME ALANI
uploaded_file = st.file_uploader("Ham CSV dosyasını (Hata Detayı) buraya yükleyin", type="csv")

if uploaded_file:
    # Veriyi Oku (Paylaştığınız formatta genellikle ilk satır başlıktır)
    df = pd.read_csv(uploaded_file)
    
    # 2. ÜST BİLGİ KARTLARI (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Kayıt", len(df))
    with col2:
        st.metric("Ort. Form Puanı", f"%{df['Ort. Form Puan'].mean():.1f}")
    with col3:
        st.metric("Benzersiz Personel", df['Personel'].nunique())
    with col4:
        st.metric("Hata Oranı Ort.", f"%{df['Hata Oranı'].mean():.1f}")

    # 3. FİLTRELEME (Kenar Çubuğu)
    st.sidebar.header("Rapor Filtreleri")
    selected_grup = st.sidebar.multiselect("Lokasyon/Grup", df['Grup Adı'].unique())
    selected_takim = st.sidebar.multiselect("Takım Lideri", df['Takım Adı'].unique())

    if selected_grup:
        df = df[df['Grup Adı'].isin(selected_grup)]
    if selected_takim:
        df = df[df['Takım Adı'].isin(selected_takim)]

    # 4. GÖRSELLEŞTİRME
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Hata Konusu Dağılımı")
        hata_fig = px.bar(df['Kriter Grup'].value_counts().reset_index(), 
                          x='index', y='Kriter Grup', 
                          labels={'index': 'Hata Kategorisi', 'Kriter Grup': 'Adet'},
                          color_discrete_sequence=['#ef553b'])
        st.plotly_chart(hata_fig, use_container_width=True)

    with c2:
        st.subheader("Takım Bazlı Performans")
        takim_fig = px.box(df, x='Takım Adı', y='Ort. Form Puan', color='Takım Adı')
        st.plotly_chart(takim_fig, use_container_width=True)

    # 5. DETAYLI TABLO
    st.subheader("🔍 Filtrelenmiş Veri Detayı")
    st.dataframe(df[['Personel', 'Takım Adı', 'Kriter', 'Hata Detayı', 'Ort. Form Puan']])

else:
    st.info("Lütfen analiz etmek için bir CSV dosyası yükleyin.")
