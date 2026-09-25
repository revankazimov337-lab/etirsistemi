import streamlit as st
import pandas as pd

# Səhifənin görünüş tənzimləmələri
st.set_page_config(page_title="Ətir Dükanı Paneli", layout="wide")

# Məlumat bazasını yaradırıq
if 'anbar' not in st.session_state:
    st.session_state.anbar = pd.DataFrame(columns=["Ətrin Adı", "Həcm (ml)", "Alış (AZN)", "Satış (AZN)", "Stok"])

st.title("🛍️ Ətir Dükanı - İdarəetmə Paneli")

# Sol tərəfdəki menyu
menyu = ["Anbar və Qazanc", "Yeni Ətir Əlavə Et", "Satış Et"]
secim = st.sidebar.radio("Bölməni seçin:", menyu)

if secim == "Anbar və Qazanc":
    st.subheader("📦 Mövcud Anbar və Gəlir Hesabatı")
    if not st.session_state.anbar.empty:
        df = st.session_state.anbar.copy()
        # Avtomatik hesablamalar
        df['Xalis Qazanc (AZN)'] = df['Satış (AZN)'] - df['Alış (AZN)']
        df['Potensial Gəlir (AZN)'] = df['Xalis Qazanc (AZN)'] * df['Stok']
        
        # Cədvəli ekranda göstəririk
        st.dataframe(df, use_container_width=True)
        
        # Ümumi statistika
        st.success(f"💰 Bütün mallar satılarsa Ümumi Gözlənilən Qazanc: **{df['Potensial Gəlir (AZN)'].sum()} AZN**")
    else:
        st.info("Anbar hələ boşdur. Sol menyudan 'Yeni Ətir Əlavə Et' bölməsinə keçin.")

elif secim == "Yeni Ətir Əlavə Et":
    st.subheader("➕ Yeni Məhsul Qeydiyyatı")
    with st.form("yeni_etir_formu"):
        ad = st.text_input("Ətrin Adı / Növü (Məs: Libre, Shaik)")
        hecm = st.text_input("Həcm (Məs: 50ml)")
        alish = st.number_input("1 ədədin Alış Qiyməti (AZN)", min_value=0.0)
        satish = st.number_input("1 ədədin Satış Qiyməti (AZN)", min_value=0.0)
        stok = st.number_input("Hazırkı Stok Miqdarı", min_value=0, step=1)
        
        tesdiq = st.form_submit_button("Anbara Əlavə Et")
        
        if tesdiq:
            yeni_setir = pd.DataFrame([{
                "Ətrin Adı": ad, "Həcm (ml)": hecm, 
                "Alış (AZN)": alish, "Satış (AZN)": satish, "Stok": stok
            }])
            st.session_state.anbar = pd.concat([st.session_state.anbar, yeni_setir], ignore_index=True)
            st.success(f"✅ {ad} anbara uğurla əlavə edildi!")

elif secim == "Satış Et":
    st.subheader("🛒 Məhsul Satışı")
    if not st.session_state.anbar.empty:
        satilacaq_etir = st.selectbox("Satılan Ətiri Seçin", st.session_state.anbar["Ətrin Adı"])
        satilan_miqdar = st.number_input("Neçə ədəd satıldı?", min_value=1, step=1)
        satish_tesdiqi = st.button("Satışı Təsdiqlə")
        
        if satish_tesdiqi:
            movcud_stok = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"].values[0]
            if movcud_stok >= satilan_miqdar:
                st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"] -= satilan_miqdar
                st.success(f"✅ Satış qeydə alındı! {satilacaq_etir} üçün stok yeniləndi.")
            else:
                st.error(f"⚠️ Anbarda cəmi {movcud_stok} ədəd {satilacaq_etir} qalıb. Sayı düzəldin.")
    else:
        st.warning("Əvvəlcə anbara məhsul əlavə edin.")
