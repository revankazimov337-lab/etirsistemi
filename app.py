import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Səhifə tənzimləmələri
st.set_page_config(page_title="Ətir Dükanı Paneli", layout="wide")

# Məlumat bazaları (Anbar və Tarixçə)
if 'anbar' not in st.session_state:
    st.session_state.anbar = pd.DataFrame(columns=["Ətrin Adı", "Həcm (ml)", "Alış (AZN)", "Satış (AZN)", "Stok"])

if 'tarixce' not in st.session_state:
    st.session_state.tarixce = pd.DataFrame(columns=["Tarix və Saat", "Əməliyyat Növü", "Ətrin Adı", "Həcm (ml)", "Miqdar", "Məbləğ (AZN)"])

if 'tesdiq_gozleyir' not in st.session_state:
    st.session_state.tesdiq_gozleyir = False

# Bakı vaxtını almaq üçün funksiya (Server vaxtını +4 saat edirik)
def baki_vaxti():
    return (datetime.utcnow() + timedelta(hours=4)).strftime("%d.%m.%Y %H:%M")

st.title("🛍️ Ətir Dükanı - İdarəetmə Paneli")

menyu = ["Anbar və Qazanc", "Yeni Ətir / Stok Əlavə Et", "Satış Et", "Əməliyyat Tarixçəsi"]
secim = st.sidebar.radio("Bölməni seçin:", menyu)

# --- 1. ANBAR BÖLMƏSİ ---
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

# --- 2. STOKA ƏLAVƏ BÖLMƏSİ ---
elif secim == "Yeni Ətir / Stok Əlavə Et":
    st.subheader("➕ Yeni Məhsul və ya Mövcud Stoka Əlavə")
    
    ad = st.text_input("Ətrin Adı / Növü (Məs: Lacoste)")
    hecm = st.text_input("Həcm (Məs: 90ml)")
    alish = st.number_input("1 ədədin Alış Qiyməti (AZN)", min_value=0.0, value=None, placeholder="Məs: 40")
    satish = st.number_input("1 ədədin Satış Qiyməti (AZN)", min_value=0.0, value=None, placeholder="Məs: 80")
    stok = st.number_input("Əlavə olunan Miqdar", min_value=1, step=1, value=None, placeholder="Məs: 10")
    
    if st.button("Yoxla və Təsdiqə Keç"):
        if not ad:
            st.error("Ətrin adını yazın!")
        elif alish is None or satish is None or stok is None:
            st.error("Qiymətləri və miqdarı tam daxil edin!")
        else:
            st.session_state.tesdiq_gozleyir = True
            st.session_state.yeni_etir_melumatlari = {"ad": ad, "hecm": hecm, "alish": alish, "satish": satish, "stok": stok}
            
    if st.session_state.tesdiq_gozleyir:
        m = st.session_state.yeni_etir_melumatlari
        exists = False
        if not st.session_state.anbar.empty:
            match = (st.session_state.anbar['Ətrin Adı'].str.lower() == m['ad'].lower()) & (st.session_state.anbar['Həcm (ml)'] == m['hecm'])
            if match.any():
                exists = True
                
        if exists:
            st.warning(f"ℹ️ '{m['ad']}' ({m['hecm']}) artıq anbarda mövcuddur. Yeni yazdığınız {m['stok']} ədəd mövcud stokun **üzərinə gələcək**.")
        else:
            st.info(f"ℹ️ '{m['ad']}' anbarda yoxdur, **yeni məhsul** kimi əlavə olunacaq.")
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Bəli, Təsdiqlə"):
                ümumi_məbləğ = m['stok'] * m['alish']
                # Tarixçəyə yazmaq üçün məlumat
                yeni_tarixce = pd.DataFrame([{
                    "Tarix və Saat": baki_vaxti(),
                    "Əməliyyat Növü": "🟢 MƏDAXİL (Anbara gəldi)",
                    "Ətrin Adı": m['ad'],
                    "Həcm (ml)": m['hecm'],
                    "Miqdar": f"+{m['stok']}",
                    "Məbləğ (AZN)": ümumi_məbləğ
                }])

                if not st.session_state.anbar.empty:
                    match = (st.session_state.anbar['Ətrin Adı'].str.lower() == m['ad'].lower()) & (st.session_state.anbar['Həcm (ml)'] == m['hecm'])
                    if match.any():
                        st.session_state.anbar.loc[match, 'Stok'] += m['stok']
                        st.session_state.anbar.loc[match, 'Alış (AZN)'] = m['alish']
                        st.session_state.anbar.loc[match, 'Satış (AZN)'] = m['satish']
                    else:
                        yeni_setir = pd.DataFrame([{"Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Alış (AZN)": m['alish'], "Satış (AZN)": m['satish'], "Stok": m['stok']}])
                        st.session_state.anbar = pd.concat([st.session_state.anbar, yeni_setir], ignore_index=True)
                else:
                    yeni_setir = pd.DataFrame([{"Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Alış (AZN)": m['alish'], "Satış (AZN)": m['satish'], "Stok": m['stok']}])
                    st.session_state.anbar = pd.concat([st.session_state.anbar, yeni_setir], ignore_index=True)
                
                # Tarixçəni yeniləyirik
                st.session_state.tarixce = pd.concat([st.session_state.tarixce, yeni_tarixce], ignore_index=True)
                
                st.success(f"✅ Uğurla əlavə olundu və tarixçəyə yazıldı!")
                st.session_state.tesdiq_gozleyir = False
        with col2:
            if st.button("❌ Ləğv Et"):
                st.session_state.tesdiq_gozleyir = False
                st.rerun()

# --- 3. SATIŞ BÖLMƏSİ ---
elif secim == "Satış Et":
    st.subheader("🛒 Məhsul Satışı")
    if not st.session_state.anbar.empty:
        satilacaq_etir = st.selectbox("Satılan Ətiri Seçin", st.session_state.anbar["Ətrin Adı"].unique())
        
        satilan_miqdar = st.number_input("Neçə ədəd satıldı?", min_value=1, step=1, value=None, placeholder="Məs: 1")
        
        if st.button("Satışı Təsdiqlə"):
            if satilan_miqdar is None:
                st.error("Zəhmət olmasa satılan miqdarı yazın!")
            else:
                movcud_stok = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"].values[0]
                if movcud_stok >= satilan_miqdar:
                    # Satışı anbardakı stokdan silirik
                    st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"] -= satilan_miqdar
                    
                    # Satış tarixçəsi üçün məlumatları çəkirik
                    satilan_hecm = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Həcm (ml)"].values[0]
                    satish_qiymeti = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Satış (AZN)"].values[0]
                    ümumi_gəlir = satilan_miqdar * satish_qiymeti
                    
                    yeni_satish = pd.DataFrame([{
                        "Tarix və Saat": baki_vaxti(),
                        "Əməliyyat Növü": "🔴 MƏXARİC (Satıldı)",
                        "Ətrin Adı": satilacaq_etir,
                        "Həcm (ml)": satilan_hecm,
                        "Miqdar": f"-{satilan_miqdar}",
                        "Məbləğ (AZN)": ümumi_gəlir
                    }])
                    st.session_state.tarixce = pd.concat([st.session_state.tarixce, yeni_satish], ignore_index=True)
                    
                    st.success(f"✅ Satış qeydə alındı! {satilan_miqdar} ədəd silindi və tarixçəyə yazıldı.")
                else:
                    st.error(f"⚠️ Anbarda cəmi {movcud_stok} ədəd {satilacaq_etir} qalıb. Satış ləğv edildi.")
    else:
        st.warning("Əvvəlcə anbara məhsul əlavə edin.")

# --- 4. TARİXÇƏ BÖLMƏSİ ---
elif secim == "Əməliyyat Tarixçəsi":
    st.subheader("📜 Bütün Mədaxil və Məxaric Tarixçəsi")
    if not st.session_state.tarixce.empty:
        # Ən son edilən əməliyyat ən üstdə görünsün
        df_tarixce = st.session_state.tarixce.copy()
        df_tarixce = df_tarixce.iloc[::-1].reset_index(drop=True)
        st.dataframe(df_tarixce, use_container_width=True)
    else:
        st.info("Hələ ki, heç bir əməliyyat edilməyib.")
