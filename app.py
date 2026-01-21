import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Operasyonel Rapor Paneli")

st.title("📂 Operasyonel Rapor Otomasyonu")

# --- DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📥 Veri Kaynaklarını Yükle")
    f_data = st.file_uploader("1. ANA VERİ (Data)", type=["xlsx"])
    f_mma = st.file_uploader("2. MMA (Data)", type=["xlsx"])
    f_sikayet = st.file_uploader("3. ŞİKAYET (Data)", type=["xlsx"])

if f_data and f_mma and f_sikayet:
    # Verileri Belleğe Alma
    df_raw = pd.read_excel(f_data)
    df_mma_raw = pd.read_excel(f_mma, sheet_name="Data")
    df_sikayet_raw = pd.read_excel(f_sikayet, sheet_name="Data")

    # --- FİLTRELEME PANELİ ---
    st.sidebar.markdown("---")
    tl_list = sorted(df_raw["Takım Adı"].unique())
    sel_tl = st.sidebar.multiselect("Takım Lideri", tl_list)
    
    loc_list = sorted(df_raw["Grup Adı"].unique())
    sel_loc = st.sidebar.multiselect("Lokasyon", loc_list)

    def apply_filters(df, tl_col, loc_col):
        if sel_tl and tl_col in df.columns:
            df = df[df[tl_col].isin(sel_tl)]
        if sel_loc and loc_col in df.columns:
            df = df[df[loc_col].isin(sel_loc)]
        return df

    # --- SEKMELER (Excel Yapısına Uygun) ---
    tabs = st.tabs(["📉 Kümüle Performans", "🎯 Hata Detayları", "🚨 Sıfırlama Kayıtları", "⭐️ MMA Sonuçları", "⚖️ Şikayet & Uyarılar"])

    with tabs[0]:
        st.subheader("Temsilci Performans Karnesi")
        f_perf = apply_filters(df_raw, "Takım Adı", "Grup Adı")
        perf_summary = f_perf.groupby("Personel")["Form Puan"].mean().reset_index()
        st.dataframe(perf_summary.sort_values("Form Puan", ascending=False), use_container_width=True)

    with tabs[1]:
        st.subheader("Hata Kırılımları ve Açıklamalar")
        f_hata = apply_filters(df_raw, "Takım Adı", "Grup Adı")
        st.dataframe(f_hata[["Personel", "Kriter", "Açıklama Detay", "Form Puan"]], use_container_width=True)

    with tabs[2]:
        st.subheader("Kritik Hatalar (Puan: 0)")
        f_sifir = apply_filters(df_raw[df_raw["Form Puan"] == 0], "Takım Adı", "Grup Adı")
        st.dataframe(f_sifir[["Personel", "Kriter", "Açıklama Detay", "Yeni Kayıt Tarihi"]], use_container_width=True)

    with tabs[3]:
        st.subheader("MMA Müşteri Geri Bildirimleri")
        f_mma = apply_filters(df_mma_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_mma[["Müşteri Temsilcisi Adı", "Soru Puan 1", "Açıklama"]], use_container_width=True)

    with tabs[4]:
        st.subheader("Şikayet ve Personel Uyarı Takibi")
        f_sik = apply_filters(df_sikayet_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_sik[["MT İsim Soyisim", "Şikayet Ana Nedeni", "Yapılacak İş Sonucu"]], use_container_width=True)

else:
    st.warning("Lütfen raporu oluşturmak için gerekli 3 dosyayı yükleyin.")
