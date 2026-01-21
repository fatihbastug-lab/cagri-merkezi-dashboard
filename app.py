import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Aralık Ayı Rapor Paneli")

st.title("❄️ Aralık Ayı Operasyonel Rapor Otomasyonu")
st.info("Yüklenen veriler sadece Aralık dönemi için işlenmektedir.")

# --- DOSYA YÜKLEME ---
with st.sidebar:
    st.header("📥 Aralık Ham Verileri")
    f_data = st.file_uploader("HAM VERİ (Aralık)", type=["xlsx"])
    f_mma = st.file_uploader("MMA (Aralık)", type=["xlsx"])
    f_sikayet = st.file_uploader("ŞİKAYET (Aralık)", type=["xlsx"])

if f_data and f_mma and f_sikayet:
    # Verileri Okuma
    df_raw = pd.read_excel(f_data)
    df_mma_raw = pd.read_excel(f_mma, sheet_name="Data")
    df_sikayet_raw = pd.read_excel(f_sikayet, sheet_name="Data")

    # --- ARALIK AYI GLOBAL FİLTRELERİ ---
    st.sidebar.markdown("---")
    tl_list = sorted(df_raw["Takım Adı"].unique())
    sel_tl = st.sidebar.multiselect("Takım Lideri", tl_list)
    
    loc_list = sorted(df_raw["Grup Adı"].unique())
    sel_loc = st.sidebar.multiselect("Lokasyon", loc_list)

    def apply_december_filters(df, tl_col, loc_col):
        if sel_tl and tl_col in df.columns:
            df = df[df[tl_col].isin(sel_tl)]
        if sel_loc and loc_col in df.columns:
            df = df[df[loc_col].isin(sel_loc)]
        return df

    # --- SEKMELER ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Aralık Performans Karnesi", 
        "🎯 Aralık Hata Detayları", 
        "🚨 Aralık Sıfırlama Kayıtları", 
        "⭐️ Aralık MMA Sonuçları", 
        "⚖️ Aralık Şikayet & Uyarılar"
    ])

    # SEKME 1: ARALIK PERFORMANS
    with tab1:
        st.subheader("Aralık Ayı Temsilci Bazlı Puan Ortalamaları")
        f_perf = apply_december_filters(df_raw, "Takım Adı", "Grup Adı")
        perf_summary = f_perf.groupby("Personel")["Form Puan"].mean().reset_index()
        st.dataframe(perf_summary.sort_values("Form Puan", ascending=False), use_container_width=True)

    # SEKME 2: HATA DETAYLARI
    with tab2:
        st.subheader("Aralık Ayı Hata Kırılımları (Total)")
        f_hata = apply_december_filters(df_raw, "Takım Adı", "Grup Adı")
        st.dataframe(f_hata[["Personel", "Kriter", "Açıklama Detay", "Form Puan"]], use_container_width=True)

    # SEKME 3: SIFIRLAMA
    with tab3:
        st.subheader("Aralık Ayı Kritik Hatalar (Puan: 0)")
        sifir_df = df_raw[df_raw["Form Puan"] == 0]
        f_sifir = apply_december_filters(sifir_df, "Takım Adı", "Grup Adı")
        st.error(f"Aralık ayında toplam {len(f_sifir)} kritik hata bulundu.")
        st.dataframe(f_sifir[["Personel", "Kriter", "Açıklama Detay", "Yeni Kayıt Tarihi"]], use_container_width=True)

    # SEKME 4: MMA
    with tab4:
        st.subheader("Aralık Ayı MMA Müşteri Geri Bildirimleri")
        f_mma = apply_december_filters(df_mma_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_mma[["Müşteri Temsilcisi Adı", "Soru Puan 1", "Açıklama", "Anket Tarihi"]], use_container_width=True)

    # SEKME 5: ŞİKAYETLER
    with tab5:
        st.subheader("Aralık Ayı Personel Şikayet Takibi")
        f_sik = apply_december_filters(df_sikayet_raw, "Takım Lideri", "Lokasyon")
        st.dataframe(f_sik[["MT İsim Soyisim", "Şikayet Ana Nedeni", "Yapılacak İş Sonucu", "Yapılacak İş Kayıt Tarihi"]], use_container_width=True)

else:
    st.warning("Lütfen Aralık ayına ait 3 ana dosyayı yükleyin.")
