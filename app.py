import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Ətir Dükanı Paneli", layout="wide")

# -- BAZALAR --
if 'anbar' not in st.session_state:
    st.session_state.anbar = pd.DataFrame(columns=["Ətrin Adı", "Həcm (ml)", "Alış (AZN)", "Satış (AZN)", "Stok"])

if 'tarixce' not in st.session_state:
    st.session_state.tarixce = pd.DataFrame(columns=["Tarix və Saat", "Əməliyyat Növü", "Ətrin Adı", "Həcm (ml)", "Miqdar", "Məbləğ (AZN)", "Qazanc (AZN)"])

if 'tesdiq_gozleyir' not in st.session_state:
    st.session_state.tesdiq_gozleyir = False

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# -- VAXT FUNKSİYALARI --
def baki_vaxti():
    return (datetime.utcnow() + timedelta(hours=4)).strftime("%d.%m.%Y %H:%M")
def bugun():
    return (datetime.utcnow() + timedelta(hours=4)).strftime("%d.%m.%Y")

st.title("🛍️ Ətir Dükanı - İdarəetmə Paneli")

# -- ADMİN GİRİŞİ (SOL MENYU) --
st.sidebar.markdown("---")
if not st.session_state.is_admin:
    st.sidebar.markdown("### 🔒 Admin Paneli")
    parol = st.sidebar.text_input("Parolu daxil edin", type="password")
    if st.sidebar.button("Giriş Et"):
        if parol == "admin123":  # PAROLU BURADAN DƏYİŞƏ BİLƏRSİNİZ
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.sidebar.error("Parol yanlışdır!")
    # İşçi üçün görünən menyu
    menyu = ["🛒 Satış Et", "📊 Gün Sonu Çıxar"]
else:
    st.sidebar.success("🔓 Admin Rejimi Açıqdır")
    if st.sidebar.button("Çıxış Et (İşçi rejiminə qayıt)"):
        st.session_state.is_admin = False
        st.rerun()
    # Admin üçün görünən tam menyu
    menyu = ["🛒 Satış Et", "📊 Gün Sonu Çıxar", "📦 Anbar və Qazanc", "➕ Yeni Ətir / Stok Əlavə Et", "📜 Əməliyyat Tarixçəsi"]

secim = st.sidebar.radio("Bölməni seçin:", menyu)
st.markdown("---")


# --- 1. SATIŞ BÖLMƏSİ (Hər kəsə açıq) ---
if secim == "🛒 Satış Et":
    st.subheader("🛒 Məhsul Satışı")
    if not st.session_state.anbar.empty and st.session_state.anbar['Stok'].sum() > 0:
        satilacaq_etir = st.selectbox("Satılan Ətiri Seçin", st.session_state.anbar.loc[st.session_state.anbar['Stok'] > 0, "Ətrin Adı"].unique())
        satilan_miqdar = st.number_input("Neçə ədəd satıldı?", min_value=1, step=1, value=None, placeholder="Məs: 1")
        
        if st.button("Satışı Təsdiqlə"):
            if satilan_miqdar is None:
                st.error("Zəhmət olmasa satılan miqdarı yazın!")
            else:
                movcud_stok = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"].values[0]
                if movcud_stok >= satilan_miqdar:
                    st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Stok"] -= satilan_miqdar
                    
                    satilan_hecm = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Həcm (ml)"].values[0]
                    satish_qiymeti = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Satış (AZN)"].values[0]
                    alish_qiymeti = st.session_state.anbar.loc[st.session_state.anbar["Ətrin Adı"] == satilacaq_etir, "Alış (AZN)"].values[0]
                    
                    ümumi_gəlir = satilan_miqdar * satish_qiymeti
                    xalis_qazanc = satilan_miqdar * (satish_qiymeti - alish_qiymeti)
                    
                    yeni_satish = pd.DataFrame([{
                        "Tarix və Saat": baki_vaxti(),
                        "Əməliyyat Növü": "🔴 MƏXARİC (Satıldı)",
                        "Ətrin Adı": satilacaq_etir,
                        "Həcm (ml)": satilan_hecm,
                        "Miqdar": f"-{satilan_miqdar}",
                        "Məbləğ (AZN)": ümumi_gəlir,
                        "Qazanc (AZN)": xalis_qazanc
                    }])
                    st.session_state.tarixce = pd.concat([st.session_state.tarixce, yeni_satish], ignore_index=True)
                    
                    st.success(f"✅ Satış qeydə alındı! Kassaya {ümumi_gəlir} AZN daxil oldu.")
                else:
                    st.error(f"⚠️ Anbarda cəmi {movcud_stok} ədəd {satilacaq_etir} qalıb.")
    else:
        st.warning("Anbarda satıla biləcək məhsul yoxdur.")

# --- 2. GÜN SONU HESABATI (Hər kəsə açıq, amma fərqli detallarla) ---
elif secim == "📊 Gün Sonu Çıxar":
    st.subheader(f"📊 Gündəlik Kassa Hesabatı ({bugun()})")
    
    if not st.session_state.tarixce.empty:
        # Yalnız bugünkü əməliyyatları süzürük
        bugunku_tarixce = st.session_state.tarixce[st.session_state.tarixce["Tarix və Saat"].str.startswith(bugun())]
        
        if not bugunku_tarixce.empty:
            satilan_mallar = bugunku_tarixce[bugunku_tarixce["Əməliyyat Növü"] == "🔴 MƏXARİC (Satıldı)"]
            
            umumi_kassa = satilan_mallar["Məbləğ (AZN)"].sum()
            satilan_eded = len(satilan_mallar) # Neçə çek
            
            st.info(f"💵 **GÜNÜN ÜMUMİ KASSASI:** {umumi_kassa} AZN")
            st.write(f"Bu gün cəmi **{satilan_eded}** satış əməliyyatı olub.")
            
            # ƏGƏR ADMİNDİRSƏ, XALİS QAZANCI DA GÖRƏCƏK
            if st.session_state.is_admin:
                xalis_qazanc = satilan_mallar["Qazanc (AZN)"].sum()
                st.success(f"💰 **GÜNÜN TƏMİZ QAZANCI:** {xalis_qazanc} AZN")
                
                alinan_mallar = bugunku_tarixce[bugunku_tarixce["Əməliyyat Növü"] == "🟢 MƏDAXİL (Anbara gəldi)"]
                xerc = alinan_mallar["Məbləğ (AZN)"].sum()
                if xerc > 0:
                    st.error(f"📉 **Bu gün mal almaq üçün xərclənən pul:** {xerc} AZN")
            
            st.markdown("**Bu gün satılan malların siyahısı:**")
            gosterilen_cedvel = satilan_mallar[["Tarix və Saat", "Ətrin Adı", "Miqdar", "Məbləğ (AZN)"]]
            st.dataframe(gosterilen_cedvel, use_container_width=True)
            
        else:
            st.warning("Bu gün heç bir əməliyyat qeydə alınmayıb.")
    else:
        st.warning("Bazada heç bir əməliyyat yoxdur.")

# --- 3. ANBAR (Yalnız Admin) ---
elif secim == "📦 Anbar və Qazanc":
    st.subheader("📦 Mövcud Anbar və Gəlir Hesabatı")
    if not st.session_state.anbar.empty:
        df = st.session_state.anbar.copy()
        df['Xalis Qazanc (AZN)'] = df['Satış (AZN)'] - df['Alış (AZN)']
        df['Potensial Gəlir (AZN)'] = df['Xalis Qazanc (AZN)'] * df['Stok']
        st.dataframe(df, use_container_width=True)
        st.success(f"💰 Bütün mallar satılarsa Ümumi Gözlənilən Qazanc: **{df['Potensial Gəlir (AZN)'].sum()} AZN**")
    else:
        st.info("Anbar hələ boşdur.")

# --- 4. STOKA ƏLAVƏ (Yalnız Admin) ---
elif secim == "➕ Yeni Ətir / Stok Əlavə Et":
    st.subheader("➕ Yeni Məhsul və ya Mövcud Stoka Əlavə")
    ad = st.text_input("Ətrin Adı / Növü (Məs: Lacoste)")
    hecm = st.text_input("Həcm (Məs: 90ml)")
    alish = st.number_input("1 ədədin Alış Qiyməti (AZN)", min_value=0.0, value=None)
    satish = st.number_input("1 ədədin Satış Qiyməti (AZN)", min_value=0.0, value=None)
    stok = st.number_input("Əlavə olunan Miqdar", min_value=1, step=1, value=None)
    
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
            if match.any(): exists = True
                
        if exists: st.warning(f"ℹ️ '{m['ad']}' anbarda mövcuddur. {m['stok']} ədəd stokun üzərinə gələcək.")
        else: st.info(f"ℹ️ '{m['ad']}' anbarda yoxdur, yeni məhsul kimi əlavə olunacaq.")
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Bəli, Təsdiqlə"):
                yeni_tarixce = pd.DataFrame([{"Tarix və Saat": baki_vaxti(), "Əməliyyat Növü": "🟢 MƏDAXİL (Anbara gəldi)", "Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Miqdar": f"+{m['stok']}", "Məbləğ (AZN)": m['stok'] * m['alish'], "Qazanc (AZN)": 0}])
                if not st.session_state.anbar.empty:
                    match = (st.session_state.anbar['Ətrin Adı'].str.lower() == m['ad'].lower()) & (st.session_state.anbar['Həcm (ml)'] == m['hecm'])
                    if match.any():
                        st.session_state.anbar.loc[match, 'Stok'] += m['stok']
                        st.session_state.anbar.loc[match, 'Alış (AZN)'] = m['alish']
                        st.session_state.anbar.loc[match, 'Satış (AZN)'] = m['satish']
                    else:
                        st.session_state.anbar = pd.concat([st.session_state.anbar, pd.DataFrame([{"Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Alış (AZN)": m['alish'], "Satış (AZN)": m['satish'], "Stok": m['stok']}])], ignore_index=True)
                else:
                    st.session_state.anbar = pd.concat([st.session_state.anbar, pd.DataFrame([{"Ətrin Adı": m['ad'], "Həcm (ml)": m['hecm'], "Alış (AZN)": m['alish'], "Satış (AZN)": m['satish'], "Stok": m['stok']}])], ignore_index=True)
                
                st.session_state.tarixce = pd.concat([st.session_state.tarixce, yeni_tarixce], ignore_index=True)
                st.success(f"✅ Uğurla əlavə olundu!")
                st.session_state.tesdiq_gozleyir = False
        with col2:
            if st.button("❌ Ləğv Et"):
                st.session_state.tesdiq_gozleyir = False
                st.rerun()

# --- 5. TARİXÇƏ (Yalnız Admin) ---
elif secim == "📜 Əməliyyat Tarixçəsi":
    st.subheader("📜 Bütün Mədaxil və Məxaric Tarixçəsi")
    if not st.session_state.tarixce.empty:
        df_tarixce = st.session_state.tarixce.copy()
        df_tarixce = df_tarixce.iloc[::-1].reset_index(drop=True)
        st.dataframe(df_tarixce, use_container_width=True)
    else:
        st.info("Hələ ki, heç bir əməliyyat edilməyib.")
