import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Excel Tabanlı Kalite & MMA Dashboard")

st.title("📊 Çağrı Merkezi Performans Analizi (Excel)")
st.info("Lütfen orijinal .xlsx formatındaki dosyalarınızı yükleyin.")

# --- DOSYA YÜKLEME ---
st.sidebar.header("📁 Excel Dosyalarını Yükle")
kalite_excel = st.sidebar.file_uploader("Kalite Detay Listesi (.xlsx)", type="xlsx")
mma_excel = st.sidebar.file_uploader("MMA Datası (.xlsx)", type="xlsx")

if kalite_excel and mma_excel:
    # Excel Sayfalarını Oku (Sayfa adı belirtilmezse ilk sayfayı okur)
    # Sizin dosyalarınızda veriler genellikle 'DATA' veya 'Data' sayfasında olduğu için:
    try:
        df_kalite = pd.read_excel(kalite_excel)
        df_mma = pd.read_excel(mma_excel)

        # Veri Eşleştirme Hazırlığı (Sicil ve Agent ID'yi metne çeviriyoruz)
        df_kalite['Sicil'] = df_kalite['Sicil'].astype(str)
        df_mma['Agent ID'] = df_mma['Agent ID'].astype(str)

        # KPI HESAPLAMALARI
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ortalama Kalite Puanı", f"%{df_kalite['Form Puan'].mean():.1f}")
        with col2:
            st.metric("MMA Memnuniyet (S1)", f"{df_mma['Soru Puan 1'].mean():.2f}")
        with col3:
            st.metric("Toplam Değerlendirme", len(df_kalite))
        with col4:
            st.metric("Toplam MMA Anketi", len(df_mma))

        st.divider()

        # --- GÖRSEL ANALİZ ---
        left, right = st.columns(2)

        with left:
            st.subheader("🏢 Takım Bazlı Kalite Performansı")
            # Takımlara göre ortalama puanlar
            takim_puan = df_kalite.groupby('Takım Adı')['Form Puan'].mean().sort_values().reset_index()
            fig_takim = px.bar(takim_puan, x='Form Puan', y='Takım Adı', orientation='h', 
                               color='Form Puan', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_takim, use_container_width=True)

        with right:
            st.subheader("💬 MMA Müşteri Geri Bildirimleri")
            # Müşteri puanlarının dağılımı (1-5 arası)
            fig_mma = px.histogram(df_mma, x="Soru Puan 1", color_discrete_sequence=['#FFA15A'], 
                                   labels={'Soru Puan 1': 'Müşteri Puanı'})
            st.plotly_chart(fig_mma, use_container_width=True)

        # --- KRİTİK HATALAR VE NOTLAR ---
        st.subheader("🔍 Detaylı İnceleme ve Koçluk Notları")
        
        # Filtreleme Seçeneği
        secili_personel = st.selectbox("Personel Seçiniz:", ["Tümü"] + list(df_kalite['Personel'].unique()))
        
        display_df = df_kalite.copy()
        if secili_personel != "Tümü":
            display_df = display_df[display_df['Personel'] == secili_personel]

        st.dataframe(display_df[['Personel', 'Takım Adı', 'Form Puan', 'Açıklama Detay', 'Dinleyen']], 
                     use_container_width=True)

    except Exception as e:
        st.error(f"Hata oluştu: {e}. Lütfen Excel dosyasındaki sütun isimlerinin doğru olduğundan emin olun.")

else:
    st.warning("Devam etmek için lütfen her iki Excel (.xlsx) dosyasını da yükleyin.")
