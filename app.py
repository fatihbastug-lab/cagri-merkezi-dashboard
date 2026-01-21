import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dinamik Operasyon Paneli")

# --- SOL PANEL: MODÜLER YÜKLEME ---
st.sidebar.header("📥 Ham Veri Yükleme")

# Dosyaları ayrı alanlarda topluyoruz
uploaded_kalite = st.sidebar.file_uploader("Kalite / Hata / Kümüle Dosyası", type="xlsx", key="k1")
uploaded_mma = st.sidebar.file_uploader("MMA Ham / Analiz Dosyası", type="xlsx", key="m1")
uploaded_risk = st.sidebar.file_uploader("Sıfırlama / Şikayet Dosyası", type="xlsx", key="r1")

# --- ANA EKRAN SEKMELERİ ---
tab_perf, tab_hata, tab_mma, tab_risk = st.tabs([
    "📈 Performans & Kümüle", 
    "🎯 Hata Detay Analizi", 
    "⭐️ Müşteri (MMA) Analizi", 
    "🚨 Kritik Vakalar"
])

# --- 1. PERFORMANS & KÜMÜLE ---
with tab_perf:
    if uploaded_kalite:
        df_kum = pd.read_excel(uploaded_kalite) # Varsayılan olarak ilk sayfa
        st.subheader("Müşteri Temsilcisi Kümüle Başarı Trendi")
        
        # Kümüle dosyasındaki sütunları otomatik bul (Son 3 Ay Ortalama vb.)
        numeric_cols = df_kum.select_dtypes(include=['number']).columns.tolist()
        name_col = next((c for c in df_kum.columns if c in ['AGENT', 'Personel', 'Müşteri Temsilcisi']), None)
        
        if name_col and numeric_cols:
            fig_kum = px.bar(df_kum.sort_values(numeric_cols[-1], ascending=False).head(20), 
                             x=name_col, y=numeric_cols[-1], color=numeric_cols[-1],
                             title="En Yüksek Performanslı Temsilciler")
            st.plotly_chart(fig_kum, use_container_width=True)
    else:
        st.info("Performans verilerini görmek için dosya yükleyin.")

# --- 2. HATA DETAY ANALİZİ ---
with tab_hata:
    if uploaded_kalite:
        # Hata detaylarını içeren sayfayı bulmaya çalışalım
        st.subheader("Hata Konuları ve Kriter Dağılımı")
        df_hata = pd.read_excel(uploaded_kalite)
        
        c1, c2 = st.columns(2)
        with c1:
            if 'Kriter Grup' in df_hata.columns:
                fig_pie = px.pie(df_hata, names='Kriter Grup', title="Hata Kategorileri")
                st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            if 'Hata Detayı' in df_hata.columns:
                hata_count = df_hata['Hata Detayı'].value_counts().reset_index().head(10)
                fig_bar = px.bar(hata_count, x='Hata Detayı', y='index', orientation='h', title="En Sık Yapılan 10 Hata")
                st.plotly_chart(fig_bar, use_container_width=True)
    
# --- 3. MMA ANALİZİ ---
with tab_mma:
    if uploaded_mma:
        df_mma = pd.read_excel(uploaded_mma)
        st.subheader("Müşteri Memnuniyet Anketi (MMA) Sonuçları")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if 'Soru Puan 1' in df_mma.columns:
                st.metric("Genel MMA Ortalaması", round(df_mma['Soru Puan 1'].mean(), 2))
                fig_mma_pie = px.pie(df_mma, names='Soru Puan 1', title="Puan Dağılımı")
                st.plotly_chart(fig_mma_pie, use_container_width=True)
        with m_col2:
            if 'Açıklama' in df_mma.columns:
                st.write("Müşteri Geri Bildirimleri")
                st.dataframe(df_mma[['Müşteri Temsilcisi Adı', 'Açıklama']].tail(10))

# --- 4. KRİTİK VAKALAR ---
with tab_risk:
    if uploaded_risk:
        df_risk = pd.read_excel(uploaded_risk)
        st.subheader("Sıfırlama Alan Çağrılar ve Risk Analizi")
        
        if 'Açıklama Detay' in df_risk.columns:
            for _, row in df_risk.head(10).iterrows():
                with st.expander(f"🔴 {row.get('Müşteri Temsilcisi', 'Personel')} - {row.get('Kriter', 'Sıfırlama')}"):
                    st.write(f"**Detay:** {row['Açıklama Detay']}")
                    st.caption(f"Tarih: {row.get('Çağrı Tarihi', 'Belirtilmemiş')}")
    else:
        st.info("Çağrı Sıfırlama verilerini yükleyin.")
