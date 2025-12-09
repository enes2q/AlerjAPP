import streamlit as st
from urun_data import urunler_listesi
import logic

st.set_page_config(page_title="Alerjen Kontrol", page_icon="🛒", layout="centered")

st.title("🛒 Alerjen Kontrol")
st.write("Ürün seç → Alerjen yaz → Kontrol Et")

# Ürünleri ismine göre haritalama
urun_map = {u["ad"]: u for u in urunler_listesi}

# 1. BÖLÜM: ÜRÜN SEÇİMİ
st.subheader("1) Ürün Seçiniz")
urun_adi = st.selectbox("Market Rafı", list(urun_map.keys()))
urun = urun_map[urun_adi]

with st.expander("ℹ️ İçindekiler Bilgisi (Göster)"):
    st.write(", ".join(urun.get("icindekiler", [])))
    if urun.get("eser_miktar"):
        st.caption("Eser miktar: " + ", ".join(urun["eser_miktar"]))

# 2. BÖLÜM: ALERJEN GİRİŞİ
st.subheader("2) Alerjen Giriniz")
alerjen = st.text_input("Alerjen (örn: süt, gluten, fındık)", placeholder="Buraya yazın...")

# 3. BÖLÜM: KONTROL BUTONU
st.subheader("3) Analiz")

if st.button("KONTROL ET 🚀", use_container_width=True):
    
    if not alerjen.strip():
        st.warning("⚠️ Lütfen bir alerjen madde giriniz.")
    else:
        # Logic dosyasındaki fonksiyonu çağırıyoruz (Ürün adını yolluyoruz)
        sonuc = logic.analiz_et(urun_adi, alerjen.strip())

        # Logic'ten gelen cevabı (KIRMIZI, TURUNCU, YESIL) kontrol ediyoruz
        durum = sonuc.get("durum")
        baslik = sonuc.get("baslik")
        mesaj = sonuc.get("mesaj")

        if durum == "HATA":
            st.error(f"HATA: {mesaj}")
            
        elif durum == "KIRMIZI":
            st.error(f"⛔ {baslik}\n\n{mesaj}")
            
        elif durum == "TURUNCU":
            st.warning(f"⚠️ {baslik}\n\n{mesaj}")
            
        elif durum == "YESIL":
            st.success(f"✅ {baslik}\n\n{mesaj}")