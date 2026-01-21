import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Entegre Kalite Dashboard")

st.title("🚀 Kurumsal Operasyonel Performans Paneli")

# --- SOL PANEL: MODÜLER DOSYA YÜKLEME ---
st.sidebar.header("📁 Veri Kaynaklarını Yükle")

# 1. Ana Rapor (Ocak Raporu - Çok Sayfalı)
main_file = st.sidebar.file_uploader("1. Ana Rapor (Ocak Raporu vb.)", type="xlsx", key="main")

# 2. Detay Liste (Günlük/Haftalık Detaylar)
detay_file = st.sidebar.file_uploader("2. Detay Liste (DATA Sayfası)", type="xlsx", key="detay")

# 3. MMA Verileri (Anket Sonuçları)
mma_file = st.sidebar.file_uploader("3. MMA Veri Seti", type="xlsx", key="mma")

# --- VERİ İŞLEME VE GÖRÜNTÜLEME ---

# Sekmeli Yapı Oluşturma
tab1, tab2, tab3, tab4 = st.tabs(["📊 Ana Rapor Analizi", "🔍 Detay Hata Analizi", "⭐️ MMA Performansı", "🚨 Kritik Vakalar"])

# --- TAB 1: ANA RAPOR (TÜM SAYFALARI OKUR) ---
with tab1:
    if main_file:
        xl = pd.ExcelFile(main_file)
        selected_sheet = st.selectbox("Görüntülemek İstediğiniz Sayfa:", xl.sheet_names)
        df_main = pd.read_excel(main_file, sheet_name=selected_sheet)
        st.write(f"### {selected_sheet} Veri Tablosu")
        st.dataframe(df_main, use_container_width=True)
    else:
        st.info("Lütfen sol panelden 'Ana Rapor' dosyasını yükleyin.")

# --- TAB 2: DETAY LİSTE ANALİZİ ---
with tab2:
    if detay_file:
        df_detay = pd.read_excel(detay_file)
        st.subheader("Hata Kriterleri Dağılımı")
        # Kalite puanı dağılımı grafiği
        fig_puan = px.histogram(df_detay, x="Form Puan", nbins=20, title="Kalite Puan Dağılımı")
        st.plotly_chart(fig_puan, use_container_width=True)
    else:
        st.info("Detay analiz için 'Detay Liste' dosyasını yükleyin.")

# --- TAB 3: MMA ANALİZİ ---
with tab3:
    if mma_file:
        df_mma = pd.read_excel(mma_excel)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MMA Genel Memnuniyet", f"{df_mma['Soru Puan 1'].mean():.2f}")
        with col2:
            fig_mma = px.pie(df_mma, names='Soru Puan 1', title="Müşteri Puan Dağılımı")
            st.plotly_chart(fig_mma, use_container_width=True)
    else:
        st.info("MMA analizlerini görmek için MMA dosyasını yükleyin.")

# --- TAB 4: KRİTİK VAKALAR (ÇAĞRI SIFIRLAMA VB.) ---
with tab4:
    if main_file:
        # Ana dosya içinde 'Sıfırlama' veya 'Şikayet' geçen sayfaları bulalım
        sheets = pd.ExcelFile(main_file).sheet_names
        risk_sheets = [s for s in sheets if "Sıfırlama" in s or "Şikâyet" in s]
        
        if risk_sheets:
            selected_risk = st.selectbox("Kritik Veri Seçin:", risk_sheets)
            df_risk = pd.read_excel(main_file, sheet_name=selected_risk)
            st.error("Düşük Performans ve Kritik Hata Kayıtları")
            st.table(df_risk.head(20))
        else:
            st.success("Kritik vaka dosyası bulunamadı.")
