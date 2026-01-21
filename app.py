import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Operasyonel Rapor Motoru")

st.title("🚀 Otomatik Kalite & Operasyon Raporu")
st.markdown("Verileri yüklediğinizde sekmeler otomatik olarak dolacaktır.")

# --- SIDEBAR: DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📂 Veri Kaynakları")
    f_data = st.file_uploader("1. HAM VERİ (Data)", type=["xlsx"])
    f_mma = st.file_uploader("2. MMA (Data)", type=["xlsx"])
    f_sikayet = st.file_uploader("3. ŞİKAYET (Data)", type=["xlsx"])

if f_data and f_mma and f_sikayet:
    # Verileri Okuma
    df_raw = pd.read_excel(f_data)
    df_mma_raw = pd.read_excel(f_mma, sheet_name="Data")
    df_sikayet_raw = pd.read_excel(f_sikayet, sheet_name="Data")

    # --- GLOBAL FİLTRELER ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Dinamik Filtreleme")
    
    # Tüm dosyalardaki ortak sütunları (Takım Lideri, Lokasyon) yakalayalım
    tl_list = sorted(df_raw["Takım Adı"].unique())
    selected_tl = st.sidebar.multiselect("Takım Lideri Seçin", tl_list)
    
    loc_list = sorted(df_raw["Grup Adı"].unique())
    selected_loc = st.sidebar.multiselect("Lokasyon Seçin", loc_list)

    # Filtreleme Fonksiyonu
    def get_filtered(df, tl_col, loc_col):
        temp = df.copy()
        if selected_tl:
            temp = temp[temp[tl_col].isin(selected_tl)]
        if selected_loc:
            temp = temp[temp[loc_col].isin(selected_loc)]
        return temp

    # --- SEKME YAPISI ---
    tabs = st.tabs([
        "📉 2023 Kümüle", 
        "🎯 Hata Detayı - Total", 
        "🚨 Çağrı Sıfırlama", 
        "⭐️ MMA Ham Data", 
        "⚖️ Şikâyet Kayıtları"
    ])

    # SEKME 1: KÜMÜLE
    with tabs[0]:
        st.subheader("M.T. Performans Özeti")
        perf = get_filtered(df_raw, "Takım Adı", "Grup Adı").groupby("Personel")["Form Puan"].mean().reset_index()
        st.dataframe(perf.sort_values("Form Puan", ascending=False), use_container_width=True)

    # SEKME 2: HATA DETAYI
    with tabs[1]:
        st.subheader("Hata Konuları ve Açıklamalar")
        f_hata = get_filtered(df_raw, "Takım Adı", "Grup Adı")
        st.dataframe(f_hata[["Personel", "Kriter", "Hata Detayı", "Açıklama Detay"]], use_container_width=True)

    # SEKME 3: ÇAĞRI SIFIRLAMA
    with tabs[2]:
        st.subheader("Kritik Hatalar (Puan Sıfırlayanlar)")
        f_sifir = df_raw[df_raw["Form Puan"] == 0]
        f_sifir = get_filtered(f_sifir, "Takım Adı", "Grup Adı")
        st.error(f"Seçili filtrelerde {len(f_sifir)} adet sıfırlama tespit edildi.")
        st.dataframe(f_sifir[["Personel", "Kriter", "Açıklama Detay", "Tarih"]], use_container_width=True)

    # SEKME 4: MMA HAM DATA
    with tabs[3]:
        st.subheader("Müşteri Geri Bildirim Detayları")
        f_mma = get_filtered(df_mma_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_mma[["Müşteri Temsilcisi Adı", "Soru Puan 1", "Açıklama"]], use_container_width=True)

    # SEKME 5: ŞİKAYETLER
    with tabs[4]:
        st.subheader("Personel Uyarı ve Şikayet Takibi")
        # Şikayet dosyasında sütun isimleri farklı olabilir, eşleştiriyoruz
        f_sik = get_filtered(df_sikayet_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_sik[["MT İsim Soyisim", "Şikayet Ana Nedeni", "Yapılacak İş Sonucu"]], use_container_width=True)

else:
    st.info("Lütfen sol taraftaki panelden 3 Excel dosyasını (Ham Veri, MMA, Şikayet) yükleyiniz.")
