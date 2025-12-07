# Verileri tuttuğumuz urun_data.py dosyasını çağırıyoruz.
# Sonra urun_data kısmındaki urunler listesi arrayi VERİTABANI adlı bir array değişkene atıyoruz ki daha rahat kullanabilelim.
import urun_data
VERITABANI = urun_data.urunler_listesi

def urun_bul(aranan_isim):
    """
    
    Bu fonksiyon, veritabanındaki ürün listesini tek tek gezer.
    İsmi eşleşen ürünü bulunca alır getirir.
    """
    # Eğer boş bir isim geldiyse hiç uğraşma, boş dön.
    if not aranan_isim: return None
    
    for urun in VERITABANI:
        # Büyük harf küçük harf sorunu olmasın diye iki tarafı da küçültüp bakıyoruz.
        if urun["ad"].lower() == aranan_isim.lower():
            return urun
            
    # Listeyi bitirdik ama ürünü bulamadık.
    return None


#  ANA MANTIK FONKSİYONU (Risk Analizi)

def analiz_et(secilen_urun_adi, kullanici_alerjisi):
    """
    Arayüz ekibinin (Grup 3) kullanacağı ana fonksiyon bu.
    Ürün adı ve alerjeni alıp, risk durumunu hesaplayıp geri yolluyoruz.
    """
    
    # 1. Adım: Seçilen ürünü veritabanından bulup getirelim.
    bulunan_urun = urun_bul(secilen_urun_adi)
    
    # Eğer ürün yoksa hata mesajı verelim ki sistem bozulmasın.
    if not bulunan_urun:
        return {
            "durum": "HATA",
            "baslik": "Ürün Bulunamadı",
            "mesaj": "Bu ürün sistemde kayıtlı değil, kontrol edip tekrar deneyin."
        }

    # 2. Adım: Veri Temizliği (Data Cleaning)
    # Kullanıcı yanlışlıkla boşluk bırakmış olabilir, siliyoruz (.strip).
    # Hepsini küçük harf yapıyoruz ki 'Süt' ile 'süt' aynı sayılsın.
    alerjen = kullanici_alerjisi.lower().strip()
    
    # Ürünün içindekiler listesini de garanti olsun diye temizliyoruz.
    icindekiler_temiz = [x.lower() for x in bulunan_urun["icindekiler"]]
    eser_miktar_temiz = [x.lower() for x in bulunan_urun["eser_miktar"]]
    
    # Ekrana basarken marka adını da gösterelim, daha düzgün dursun.
    marka_adi = bulunan_urun.get("marka", "Marka Yok")


    # 3. Adım: Karşılaştırma (Algoritma Burada Çalışıyor)

    # SENARYO 1: KESİN İÇERİK KONTROLÜ
    # Alerjen madde direkt içindekiler listesinde var mı?
    for madde in icindekiler_temiz:
        if alerjen in madde:
            # Bulduk! Bu ürün kesinlikle yasak.
            return {
                "durum": "KIRMIZI",
                "baslik": "🔴 YASAK! (Tüketmeyin)",
                "mesaj": f"DİKKAT! **{marka_adi} - {bulunan_urun['ad']}** ürününde doğrudan **'{madde}'** var."
            }

    # SENARYO 2: ESER MİKTAR (BULAŞMA) KONTROLÜ
    # İçine konmamış ama üretim bandından bulaşma riski var mı?
    for madde in eser_miktar_temiz:
        if alerjen in madde:
            # Riskli durum. Uyarı veriyoruz.
            return {
                "durum": "TURUNCU",
                "baslik": "🟠 RİSKLİ (Eser Miktar)",
                "mesaj": f"Ürün içeriğinde yok ama üretim hattından **'{madde}'** bulaşma riski var."
            }

    # SENARYO 3: TEMİZ
    # Yukarıdaki iki kontrolden de geçtiyse ürün güvenlidir.
    return {
        "durum": "YESIL",
        "baslik": "🟢 GÜVENLİ GÖRÜNÜYOR",
        "mesaj": f"**{marka_adi} - {bulunan_urun['ad']}** içeriğinde **'{alerjen}'** tespit edilmedi."
    }


#  TEST ALANI (Sadece biz çalıştırınca görünür)
# Bu dosyayı doğrudan çalıştırdığımızda burası devreye girer.
# Arayüz bitmeden kodumuzu buradan test edip emin olabiliriz.

if __name__ == "__main__":
    print("\n--- TEST MODU BAŞLADI ---")
    
    # Test 1: İçinde fındık olan bir ürünle deneme.
    sonuc1 = analiz_et("Ülker Çikolatalı Gofret", "Fındık")
    print(f"Test 1 (Gofret + Fındık): {sonuc1['baslik']}")
    
    # Test 2: Temiz olması gereken bir durum.
    sonuc2 = analiz_et("Coca-Cola Zero", "Süt")
    print(f"Test 2 (Cola + Süt): {sonuc2['baslik']}")

    print("--- TEST BİTTİ ---")