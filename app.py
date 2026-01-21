import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Master Operasyon Dashboard")

st.title("🚀 Kurumsal Çağrı Merkezi 360° Analiz Paneli")
st.markdown("Ocak Raporu, MMA ve Detay Listelerin tamamını içeren entegre sistem.")

# --- DOSYA YÜKLEME ---
st.sidebar.header("📁 Veri Kaynakları")
uploaded_file = st.sidebar.file_uploader("Ana Excel Dosyasını Yükle (Ocak Raporu vb.)", type="xlsx")

if uploaded_file:
    # 1. Dosyadaki tüm sayfaları oku
    xl = pd.ExcelFile(uploaded_file)
    all_sheets = xl.sheet_names
    
    st.sidebar.success(f"Dosya Okundu: {len(all_sheets)} sayfa bulundu.")
    
    # 2. Sayfa Seçimi
    selected_page = st.sidebar.radio("Görüntülemek İstediğiniz Analiz:", all_sheets)
    
    # Veriyi yükle (İlk birkaç satırı atlama gerekebilir, kod bunu otomatik dener)
    df = pd.read_excel(uploaded_file, sheet_name=selected_page)
    
    # Veri Temizleme: Eğer üstte boş satırlar varsa temizle
    if df.columns.str.contains('Unnamed').any() or df.iloc[0:2].isnull().all().any():
        df = pd.read_excel(uploaded_file, sheet_name=selected_page, header=1) # Genelde 1. veya 2. satır başlıktır

    # --- DİNAMİK DASHBOARD ALANLARI ---
    
    # A. Hata Detayları veya Outbound Sayfaları İçin (Grafik Odaklı)
    if "Hata" in selected_page or "Detay" in selected_page:
        st.subheader(f"⚠️ {selected_page} - Kırılım Analizi")
        
        c1, c2 = st.columns(2)
        with c1:
            if 'Kriter Grup' in df.columns:
                fig = px.pie(df, names='Kriter Grup', title="Hata Kategorileri", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'Takım Adı' in df.columns:
                fig2 = px.bar(df['Takım Adı'].value_counts().reset_index(), x='index', y='Takım Adı', title="Takım Bazlı Hata Sayıları")
                st.plotly_chart(fig2, use_container_width=True)

    # B. Kümüle Performans Sayfaları İçin (Trend Odaklı)
    elif "Kümüle" in selected_page:
        st.subheader(f"📈 {selected_page} - Performans Trendi")
        # Sayısal sütunları bul (Puanlar)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if 'AGENT' in df.columns or 'Personel' in df.columns:
            name_col = 'AGENT' if 'AGENT' in df.columns else 'Personel'
            st.write("En Yüksek Puanlı İlk 15 Temsilci")
            fig3 = px.bar(df.sort_values(by=numeric_cols[-1], ascending=False).head(15), 
                          x=name_col, y=numeric_cols[-1], color=numeric_cols[-1])
            st.plotly_chart(fig3, use_container_width=True)

    # C. Çağrı Sıfırlama veya Şikayet Sayfaları İçin (Kritik Uyarılar)
    elif "Sıfırlama" in selected_page or "Şikâyet" in selected_page:
        st.subheader(f"🚨 {selected_page} - Kritik Vakalar")
        if 'Açıklama Detay' in df.columns:
            for i, row in df.head(5).iterrows():
                st.error(f"**Personel:** {row.get('Müşteri Temsilcisi', 'Bilinmiyor')} | **Kriter:** {row.get('Kriter', 'Sıfırlama')}")
                st.caption(f"Detay: {row['Açıklama Detay']}")

    # D. Genel Veri Tablosu Görüntüleme
    st.markdown("---")
    st.subheader("🔍 Tüm Veri Tablosu")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Lütfen tüm sayfaları analiz etmek için Excel dosyanızı yükleyin.")
