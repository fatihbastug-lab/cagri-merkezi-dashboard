import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Kalite & MMA Dashboard")

# Yan Panel: Dosya Yükleme
st.sidebar.title("📁 Veri Girişi")
kalite_file = st.sidebar.file_uploader("Kalite Detay Listesini Yükle", type="csv")
mma_file = st.sidebar.file_uploader("MMA Datasını Yükle", type="csv")

# Veri İşleme Fonksiyonu
if kalite_file and mma_file:
    df_kalite = pd.read_csv(kalite_file)
    df_mma = pd.read_csv(mma_file)

    # Özet Sayfası
    st.title("🎯 Operasyonel Performans Özeti")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Kalite Puan Dağılımı")
        fig1 = px.histogram(df_kalite, x="Form Puan", nbins=20, color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("MMA Müşteri Puanları (Soru 1)")
        fig2 = px.pie(df_mma, names="Soru Puan 1", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    # Kritik Tespitler
    st.divider()
    st.subheader("⚠️ MMA Tespit ve Aksiyon Analizi")
    # MMA dosyasındaki 'Açıklama' sütunundan kritik kelimeleri çekme
    st.table(df_mma[['Müşteri Temsilcisi Adı', 'Çağrı Konusu', 'Açıklama']].tail(10))
