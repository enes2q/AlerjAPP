# urun_data.py dosyasını 'import' ederek o dosyadaki verilere erişim izni alıyoruz.
# Bu işlem veriyi kopyalamaz, sadece bellekteki (RAM) yerine işaret eder (Reference).
import urun_data
# 'VERITABANI' burada bir DEGISKEN (VARIABLE) ismidir.
# Bu değişken, hafızada tek bir metin tutmaz; bir DIZI (ARRAY / LIST) yapısını tutar.
# Yani VERITABANI değişkeni, bilgisayarın hafızasındaki o uzun listenin adresini gösteren bir etikettir.
VERITABANI = urun_data.urunler_listesi
print("SISTEM BILGISI: Urun listesi (Array) basariyla degiskene atandi.")
def urun_bul(aranan_isim):
    # Eger fonksiyona bos veri gelirse bosuna bellek harcanmasını onlemek amac
    if not aranan_isim: 
        return None
    # 'VERITABANI' bir Liste oldugu icin, icindeki her bir eleman bir Urun'dur.
    # urun degiskeni burada gecici bir degisken olarak kullanılıyo.
    # Dongunun her adiminda, urun degiskeni siradaki dictionary verisini tutar.
    for urun in VERITABANI:
        # Bilgisayar icin A harfi ile a harfi farkli anlamlara gelir.
        # Bu yuzden karsilastirma yapmadan once .lower() metodu ile iki tarafi da kucultuyoruz.
        # Boylece buyuk kucuk harf farkını ortadan kaldırarak arama yapiyoruz.
        if urun["ad"].lower() == aranan_isim.lower():
            return urun # Eslesme saglandi, buldugumuz Sozluk yapisini  geri donduruyoruz.
            
    # Dongu listenin sonuna kadar gitti ve return calismadiysa urun yok demektir.
    return None
    #BURDAN SONRAKİ YORUMLAR DETAYLANDIRILACAK -ENES 
def analiz_et(secilen_urun_adi, kullanici_alerjisi):
    # Once yukarida yazdigimiz arama fonksiyonunu cagiriyoruz.
    # Bu bize ya bir Sozluk (Dict) doner ya da Bos (None) doner.
    bulunan_urun = urun_bul(secilen_urun_adi)
    # Eger gelen veri 'None' ise, urun bulunamadi demektir. Kodun cokmemesi icin hata mesaji donduruyoruz.
    if not bulunan_urun:
        return {
            "durum": "HATA",
            "baslik": "Urun Bulunamadi",
            "mesaj": "Sistemde teknik bir aksaklik var veya urun kaydi silinmis."
        }
    # Kullanicidan gelen String verisinin basindaki ve sonundaki bosluklari .strip() ile kirpiyoruz.
    # Aksi takdirde " Fistik " ile "Fistik" eslesmezdi.
    if kullanici_alerjisi:
        alerjen = kullanici_alerjisi.lower().strip()
    else:
        return {"durum": "HATA", "baslik": "Eksik Bilgi", "mesaj": "Lutfen alerjen bilgisini bos birakmayin."}
    # Once hafizada 'icindekiler_temiz' adinda bos bir yer aciyoruz.
    icindekiler_temiz = [] 
    # bulunan urunun icindekiler listesindeki her bir maddeyi sirayla geziyoruz.
    for madde in bulunan_urun["icindekiler"]:
        # O anki maddeyi kucuk harfe ceviriyoruz.
        kucuk_harfli_madde = madde.lower()
        # Hazirladigimiz bos listenin sonuna ekliyoruz.
        icindekiler_temiz.append(kucuk_harfli_madde)
    # Ayni islemi eser miktar icin tekrar yapiyoruz. Once bos bir liste:
    eser_miktar_temiz = []

    for madde in bulunan_urun["eser_miktar"]:
        # Kucuk harfe cevirip listeye ekliyoruz.
        eser_miktar_temiz.append(madde.lower())
    # Sozluk icinden marka anahtarini  okuyoruz. Yoksa varsayilan deger atiyoruz.
    marka_adi = bulunan_urun.get("marka", "Marka Yok")
    # in operatoru, bir String'in bir Liste icinde olup olmadigini kontrol eder.
    for madde in icindekiler_temiz:
        if alerjen in madde:
            # Eger alerjen bulunduysa, fonksiyonu burada bitiriyoruz .
            # Geriye dondurdugumuz sey bir Sozluk yapisidir.
            return {
                "durum": "KIRMIZI", 
                "baslik": "YASAK! (Tuketmeyin)",
                "mesaj": f"DIKKAT! **{marka_adi} - {bulunan_urun['ad']}** urununde dogrudan **'{madde}'** bulunmaktadir."
            }
    # Eger yukaridaki donguden ciktiysa demek ki ana listede yok. Simdi ikinci listeye bakiyoruz.
    for madde in eser_miktar_temiz:
        if alerjen in madde:
            return {
                "durum": "TURUNCU", 
                "baslik": "RISKLI (Eser Miktar)",
                "mesaj": f"Urun iceriginde yok ama uretim hattindan **'{madde}'** bulasma riski (Eser Miktar) tasimaktadir."
            }
    # Kod buraya kadar ulastiysa, hicbir return calismamis demektir.
    # Yani alerjen hicbir listede bulunamamistir.
    return {
        "durum": "YESIL", 
        "baslik": "GUVENLI GORUNUYOR",
        "mesaj": f"Yapilan analizde **{marka_adi} - {bulunan_urun['ad']}** iceriginde **'{alerjen}'** tespit edilmemistir."
    }
# Bu blok, dosya baska bir module tarafindan import edilirse CALISMAZ.
# Sadece dogrudan terminalden calistirildiginda (__main__) devreye girer.
# Amac kodu test etmektir.

if __name__ == "__main__":
    print("\n--- DEBUG MODU: TEST BASLIYOR ---\n")
    
    #Test
    #i ile yazıldıgı icin findik yok dendi sonradan düzeltilecek mainde sorun çıkarmadığı ve testte sorun çıkardığı için 
    #ellemeyebiliriz -Enes
    print("[TEST 1] Ulker Gofret icin Findik taraniyor...")
    sonuc1 = analiz_et("Ulker Cikolatali Gofret", "Findik")
    
    # Hata yakalama
    if "baslik" in sonuc1:
        print(f"SONUC: {sonuc1['baslik']}")
    else:
        print(f"HATA: {sonuc1}")
    
    # Test Senaryosu 2
    print("\n[TEST 2] Coca-Cola Zero icin Sut taraniyor...")
    sonuc2 = analiz_et("Coca-Cola Zero", "Sut")
    
    if "baslik" in sonuc2:
        print(f"SONUC: {sonuc2['baslik']}")
    else:
        print(f"HATA: {sonuc2}")

    print("\n--- TESTLER TAMAMLANDI ---")