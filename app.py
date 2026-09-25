import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ətir Dükanı Paneli", layout="wide")

# Məlumat bazaları
if 'anbar' not in st.session_state:
    st.session_state.anbar = pd.DataFrame(columns=["Ətrin Adı", "Həcm (ml)", "Alış (AZN)", "Satış (AZN)", "Stok"])

if 'tesdiq_gozleyir' not in st.session_state:
    st.session_state.tesdiq_gozleyir = False

st.title("🛍️ Ətir Dükanı - İdarəetmə Paneli")

menyu = ["Anbar və Qazanc", "Yeni Ətir Əlavə Et", "Satış Et"]
secim = st.sidebar.radio("Bölməni seçin:", menyu)

if secim == "Anbar və Qazanc":
    st.subheader("📦 Mövcud Anbar və Gəlir Hesabatı")
    if not st.session_state.anbar.empty:
        df = st.session_state.anbar.copy()
        df['Xalis Qazanc (AZN)'] = df['Satış (AZN)'] - df['Alış (AZN)']
        df['Potensial Gəlir (AZN)'] = df['Xalis Qazanc (AZN)'] * df['Stok']
        
        st.dataframe(df, use_container_width=True)
        st.success(f"💰 Bütün mallar satılarsa Ümumi Gözlənilən Qazanc: **{df['Potensial Gəlir (AZN)'].sum()} AZN**")
    else:
        st.info("Anbar hələ boşdur.")

elif secim == "Yeni Ətir Əlavə Et":
    st.subheader("➕ Yeni Məhsul Qeydiyyatı")
    
    ad = st.text_input("Ətrin Adı / Növü (Məs: Libre, Shaik)")
    hecm = st.text_input("Həcm (Məs: 50ml)")
    alish = st.number_input("1 ədədin Alış Qiyməti (AZN)", min_value=0.0)
    satish = st.number_input("1 ədədin Satış Qiyməti (AZN)", min_value=0.0)
    stok = st.number_input("Hazırkı Stok Miqdarı", min_value=0, step=1)
    
    # Əgər ətir bazada varsa xəbərdarlıq edirik
    if not st.session_state.anbar.empty and ad in st.session_state.anbar['Ətrin Adı'].values:
        st.warning(f"⚠️ '{ad}' adlı ətir artıq bazada mövcuddur! (Əgər sadəcə mal gəlibsə, onu başqa bölmədə artıracağıq).")
    
    if st.button("Anbara Əlavə Et"):
        if ad == "":
            st.error("Ətrin adını yazın!")
        else:
            st.session_state.tesdiq_gozleyir = True
            st.session_state.yeni_etir_melumatlari = {"ad": ad, "hecm": hecm, "alish": alish, "satish": satish, "stok": stok}
            
    # İkinci təsdiq pəncərəsi
    if st.session_state.tesdiq_gozleyir:
        m = st.session_state.yeni_etir_melumatlari
        st.info(f"❓ **{m['ad']}** ətrini anbara əlavə etmək istədiyinizə əminsiniz?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Bəli, Təsdiqlə və Əlavə Et"):
                yeni_setir = pd.DataFrame([{"Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Alış (AZN)": m['alish'], "Satış (AZN)": m['satish'], "Stok": m['stok']}])
                st.session_state.anbar = pd.concat([st.session_state.anbar, yeni_setir], ignore_index=True)
                st.session_state.tesdiq_gozleyir = False
                st.success(f"✅ {m['ad']} anbara uğurla əlavə edildi!")
        with col2:
            if st.button("❌ Xeyr, Ləğv Et"):
                st.session_state.tesdiq_gozleyir = False
                st.rerun()

elif secim == "Satış Et":
    st.subheader("🛒 Məhsul Satışı")
    if not st.session_state.anbar.empty:
        satilacaq_etir = st.selectbox("Satılan Ətiri Seçin", st.session_state.anbar["Ətrin Adı"])
        satilan_miqdar = st.number_input("Neçə ədəd satıldı?", min_value=1, step=1)
        
        if st.button("Satışı Təsdiqlə"):
            movcud_stok = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"].values[0]
            if movcud_stok >= satilan_miqdar:
                st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"] -= satilan_miqdar
                st.success(f"✅ Satış qeydə alındı! {satilacaq_etir} ətrindən {satilan_miqdar} ədəd silindi.")
            else:
                st.error(f"⚠️ Anbarda cəmi {movcud_stok} ədəd {satilacaq_etir} qalıb.")
    else:
        st.warning("Əvvəlcə anbara məhsul əlavə edin.")
        
