import streamlit as st
# logic.py dosyasini cagiriyoruz. Burasi uygulamanin beyni (backend) sayilir.
# Arayuz kodlariyla islem kodlarini ayirmak (Separation of Concerns) yazilim mimarisi acisindan onemlidir.
# Arayuz sadece gosterir, logic dosyasi ise hesaplar ve veri ceker.
import logic

# Sayfanin tarayici sekmesinde gorunecek adini, ikonunu ve genel duzenini ayarliyoruz.
# layout="centered" parametresi ozellikle mobil cihazlardan girildiginde
# icerigin ekrana ortalanmasini ve daha duzgun gorunmesini saglar.
st.set_page_config(page_title="Alerjen Kontrol", page_icon="A", layout="centered")

# Sayfanin ana basligi ve kullaniciyi yonlendiren kisa bir bilgi notu.
st.title("Alerjen Kontrol")
st.write("Barkod gir -> Alerjen yaz -> Kontrol et")

# Kullanicidan veri aldigimiz input alanlari.
# Burayi adim adim numaralandirdik ki kullanici akisi kolay takip edebilsin.

st.subheader("1) Barkod Giriniz")
# text_input ile kullanicidan barkod verisini string (metin) olarak aliyoruz.
# placeholder ile kutunun icine silik bir ornek yazarak kullaniciya ne girmesi gerektigini gosteriyoruz.
barcode = st.text_input("Barkod", placeholder="Orn: 3017624010701")

st.subheader("2) Alerjen Giriniz")
# Kullanicinin alerjisini soruyoruz. Burasi da serbest metin girisi.
alerjen = st.text_input("Alerjen (orn: sut, gluten, findik)", placeholder="Buraya yazin...")

st.subheader("3) Analiz")

# Butona basildigi anda altindaki kod blogu calismaya baslar.
# use_container_width=True sayesinde buton bulundugu alani tam kaplar, mobilde daha kolay tiklanir.
if st.button("KONTROL ET", use_container_width=True):
    
    # Input Validation (Giris Kontrolu):
    # Kullanici bos veri gonderip sistemi yormasin veya hataya sebep olmasin diye on kontrol yapiyoruz.
    # .strip() metodu, kullanicinin yanlislikla bastaki veya sondaki bosluklara basmasini temizler.
    if not barcode.strip():
        st.warning("Lutfen barkod giriniz.")
    elif not alerjen.strip():
        st.warning("Lutfen alerjen giriniz.")
    else:
        # Eger girdiler doluysa logic dosyasindaki analiz fonksiyonunu cagiriyoruz.
        # Bu fonksiyon internete gidip veriyi cekecek ve bize sonucu getirecek.
        # Bu islem senkron (sirali) calisir, yani sonuc gelene kadar kod bir alt satira gecmez.
        sonuc = logic.analiz_et(barcode.strip(), alerjen.strip())

        # Logic dosyasindan donen veriyi (Dictionary yapisini) parcalayip degiskenlere aliyoruz.
        # .get() kullaniyoruz ki eger sozlukte o anahtar yoksa program patlamasin, None donsun.
        # Bu, "Defensive Programming" (Savunmaci Programlama) mantigidir.
        durum = sonuc.get("durum")
        baslik = sonuc.get("baslik", "")
        mesaj = sonuc.get("mesaj", "")

        # Logic tarafindan gelen durum koduna (status code) gore arayuzde farkli renkte kutular gosteriyoruz.
        # Kullanici metni okumasa bile rengine bakarak sonucu anlayabilmeli (Visual Feedback).
        
        if durum == "HATA":
            # API baglantisi koparsa veya urun bulunamazsa kirmizi hata mesaji gosteriyoruz.
            st.error(mesaj)
            
        elif durum == "KIRMIZI":
            # Yasakli madde tespit edildiginde st.error kullanarak dikkat cekici kirmizi bir alan olusturuyoruz.
            # \n\n karakteri ile baslik ve mesaj arasina bosluk birakarak okunabilirligi artiriyoruz.
            st.error(baslik + "\n\n" + mesaj)
            
        elif durum == "TURUNCU":
            # Eser miktar veya bulasma riski varsa st.warning ile sari/turuncu uyari veriyoruz.
            # Bu, "Yasak degil ama dikkatli ol" anlamina gelir.
            st.warning(baslik + "\n\n" + mesaj)
            
        elif durum == "YESIL":
            # Herhangi bir risk bulunmadiginda st.success ile yesil onay kutusu gosteriyoruz.
            st.success(baslik + "\n\n" + mesaj)
            
        else:
            # Eger yukaridaki durumlarin hicbiri degilse (beklenmeyen bir kod gelirse),
            # st.info ile mavi bir bilgilendirme kutusu gosteriyoruz.
            st.info("Beklenmeyen durum degeri alindi.")