import requests

# API'nin ana adresi. Bunu en tepeye sabitliyoruz ki yarin obur gun adres degisirse
# kodun icinde 50 farkli yeri arayip degistirmekle ugrasmayalim. Tek yerden yonetelim.
BASE = "https://world.openfoodfacts.org/api/v2"

# Burasi bizim ceviri merkezimiz. Kullanici "sut" yazar ama API veritabaninda bu "milk", "lactose" 
# veya "whey" olarak gecer. O yuzden bir sozluk (dictionary) yapisi kurduk.
# Listeleri koseli parantezde tuttuk cunku bir alerjenin birden fazla karsiligi olabiliyor.
# Ornegin "findik" arayan biri icin hem "hazelnut" hem de genel "nuts" uyarilarina bakmamiz lazim.
TR2EN = {
    "sut": ["milk", "lactose", "whey", "dairy"],     # Süt türevleri
    "süt": ["milk", "lactose", "whey", "dairy"],     # Türkçe karakterli hali
    "peynir": ["cheese", "milk"],                    # Peynir de süttür
    "yogurt": ["yogurt", "milk"],
    "tereyag": ["butter", "milk"],
    
    # Kuruyemisler (Burada coklu etiket mantigi onemli: Hem ozele hem genele bakiyoruz)
    "findik": ["hazelnut", "nuts"], 
    "fındık": ["hazelnut", "nuts"], 
    "fistik": ["pistachio", "nuts"], 
    "fıstık": ["pistachio", "nuts"],
    "yer fistigi": ["peanuts", "nuts"],
    "badem": ["almonds", "nuts"],
    "ceviz": ["walnuts", "nuts"],
    "kaju": ["cashew", "nuts"],
    
    # Tahillar
    "gluten": ["gluten", "wheat", "barley", "rye", "oats"], # Gluten iceren her sey
    "bugday": ["wheat", "gluten"],
    
    # Digerleri
    "balik": ["fish"],
    "yumurta": ["eggs", "egg"],
    "soya": ["soybeans", "soy"],
}

# Gelen metni bilgisayarin anlayacagi standarta indirgeyen fonksiyon.
# Bilgisayar icin "Süt" ve "sut" tamamen farkli seylerdir (ASCII kodlari farkli).
# Biz burada hepsini kucuk harfe ve Ingilizce karaktere cevirip esitliyoruz ki karsilastirma hatasi olmasin.
def metni_temizle(metin):
    # Eger gelen veri bos (None) ise islem yapmaya calisip programi cokertmeyelim.
    # Bos bir string donup fonksiyonu guvenli sekilde bitiriyoruz (Guard Clause).
    if not metin: 
        return "" 

    # Karakter degisim tablosu. Turkce karakterleri Ingilizce karsiliklariyla degistiriyoruz.
    # replace() yerine maketrans() kullandik cunku buyuk verilerde daha performansli calisiyor.
    ceviri = str.maketrans("ğĞüÜşŞıİöÖçÇ", "gGuUsSiIoOcC")
    
    # Sirasiyla: Karakterleri degistir -> Kucuk harfe cevir -> Bastaki sondaki bosluklari sil.
    return metin.translate(ceviri).lower().strip()

# Barkodu alip internetten urunu getiren ana fonksiyonumuz.
def api_urun_bul(barcode):
    # Once barkodu temizliyoruz, kullanici yanlislikla bosluk birakmis olabilir.
    barcode = (barcode or "").strip()
    
    # Eger barkod bos geldiyse sunucuyu bosuna mesgul etmeyelim, direkt donelim.
    if not barcode: 
        return None 

    # F-string teknigi ile dinamik URL olusturuyoruz.
    url = f"{BASE}/product/{barcode}"
    
    # Optimizasyon: API'den butun veriyi (resimler, ulkeler vs.) istemiyoruz.
    # Sadece isim, marka ve icindekiler lazim. Boylece hem veri tasarrufu yapiyoruz hem de hiz kazaniyoruz.
    params = {"fields": "product_name,brands,ingredients,traces_tags,allergens_tags,ingredients_text"}

    # Try-Except Blogu: Internet kesik olabilir, sunucu cevap vermeyebilir veya cok yavas olabilir.
    # Bu blok sayesinde program hata verip kapanmak yerine kontrollu bir sekilde yonetiliyor.
    try:
        # requests.get ile internet kapisini calip "Veriyi ver" diyoruz.
        # timeout=8 parametresi onemli: "8 saniye cevap gelmezse pes et, programi dondurma."
        r = requests.get(url, params=params, timeout=8)
        
        # Eger sunucu 404 (Bulunamadi) veya 500 (Sunucu Hatasi) donerse hata firlatiyoruz.
        r.raise_for_status()
        
        # Gelen veri JSON formatindadir. Bunu Python'un anlayacagi Sozluge (Dictionary) ceviriyoruz.
        data = r.json()
    except:
        # Baglanti hatasi olursa sessizce None donuyoruz, kullaniciya karmasik hata kodlari gostermiyoruz.
        return None

    # Gelen paketin icinden asil urun verisini cikariyoruz.
    product = data.get("product")
    
    # Barkod hataliysa API bos donebilir. Kontrol sart.
    if not product: 
        return None

    # Veri Cekme: .get() kullaniyoruz ki anahtar yoksa hata vermesin, varsayilan deger ("Marka Yok") donsun.
    # Bu sayede kodumuz daha dayanikli (robust) oluyor.
    ad = product.get("product_name") or "İsimsiz Ürün"
    marka = product.get("brands") or "Marka Yok"

    # --- İçindekiler Listesini Hazirlama ---
    icindekiler = []
    # API bazen listeyi duzgun veriyor, once onu deniyoruz.
    ingredients = product.get("ingredients") or []
    
    # Listenin icindeki her bir maddeyi sirayla geziyoruz (Iteration).
    for ing in ingredients:
        txt = ing.get("text") # Maddenin ismini al.
        if txt: # Eger isim bos degilse listemize ekle.
            icindekiler.append(txt)
    
    # Yedek Plan (Fallback): Eger yukaridaki liste bos geldiyse, duz metin alanina bakiyoruz.
    # Bazen veritabaninda listeyi ayirmamis oluyorlar, duz yazi olarak duruyor.
    if not icindekiler:
        txt = product.get("ingredients_text", "")
        if txt: 
            icindekiler = [txt] # Metni tek elemanli bir liste haline getiriyoruz.

    # --- VERİ TEMİZLİĞİ (Data Cleaning) ---
    # API bize verileri "en:nuts", "fr:lait" gibi dil kodlariyla veriyor.
    # Bizim sadece iki noktadan sonraki temiz kelimeye ihtiyacimiz var.
    
    # 1. Eser Miktar (Traces) Temizligi
    traces = [] # Temizlenmis verileri koyacagimiz bos sepet.
    ham_traces_listesi = product.get("traces_tags") or []
    
    # Ham listeyi tek tek geziyoruz.
    for t in ham_traces_listesi:
        # Gelen verinin yazi (string) oldugundan emin oluyoruz, bazen sayi gelebilir, hata olmasin.
        if isinstance(t, str):
            # .split(":", 1) metni ikiye boler. Örn: "en:nuts" -> ["en", "nuts"]
            # [-1] ile listenin son elemanini yani "nuts" kismini aliyoruz.
            temiz_veri = t.split(":", 1)[-1]
            traces.append(temiz_veri)

    # 2. Resmi Alerjenler (Allergens) Temizligi
    allergens = [] # Yeni bos sepet.
    ham_allergens_listesi = product.get("allergens_tags") or []
    
    for a in ham_allergens_listesi:
        if isinstance(a, str):
            # Yine ayni temizlik islemi: "en:milk" -> "milk"
            temiz_veri = a.split(":", 1)[-1]
            allergens.append(temiz_veri)

    # Topladigimiz ve temizledigimiz veriyi paketleyip ana fonksiyona geri yolluyoruz.
    return {
        "ad": ad,
        "marka": marka,
        "icindekiler": icindekiler,
        "eser_miktar": traces,
        "alerjenler": allergens
    }

# BEYIN KISMI: Barkodu ve alerjeni alip karsilastirmayi yapan ana fonksiyon.
def analiz_et(barkod, kullanici_alerjisi):
    # Once yukaridaki API fonksiyonunu cagirip urunu buluyoruz.
    bulunan_urun = api_urun_bul(barkod)
    
    # Urun bulunamazsa islem yapmanin anlami yok, hata donuyoruz.
    if not bulunan_urun:
        return {"durum": "HATA", "baslik": "Ürün Bulunamadı", "mesaj": "Barkod hatalı veya ürün kayıtlı değil."}

    # Alerjen girilmemisse neyi arayacagimizi bilemeyiz.
    if not kullanici_alerjisi:
        return {"durum": "HATA", "baslik": "Eksik Bilgi", "mesaj": "Alerjen girmediniz."}

    # Kullanicinin girdigi veriyi standart hale getiriyoruz (süt -> sut).
    alerjen_raw = metni_temizle(kullanici_alerjisi)
    
    # --- Kelime Genisletme (Mapping) ---
    # TR2EN sozlugunden bakiyoruz. Eger kelime sozlukte varsa Ingilizce karsiliklarini (liste olarak) al.
    # Eger yoksa (orn: kivi), kullanicinin yazdigini liste icine koyup devam et.
    # Boylece hem "findik" hem de "nuts" arayabilecegiz.
    aranacak_etiketler = TR2EN.get(alerjen_raw, [alerjen_raw])
    
    # Kodun asagisinda surekli sozlukten cagirmamak icin degiskenlere atiyoruz, okumasi kolay olsun.
    marka_adi = bulunan_urun.get("marka", "Marka Yok")
    urun_adi = bulunan_urun.get("ad", "İsimsiz Ürün")
    
    # --- VERİ HAZIRLIĞI (Normalization) ---
    # Karsilastirma yaparken "Milk" ile "milk" eslesmez. O yuzden API'den gelen verileri de kucultuyoruz.
    # Burada for dongusu kullaniyoruz ki adim adim ne yaptigimiz gorulsun.

    # 1. Resmi Alerjen Listesini Kucultme
    urun_resmi_alerjenler = []
    for ham_alerjen in bulunan_urun["alerjenler"]:
        temiz_alerjen = ham_alerjen.lower()
        urun_resmi_alerjenler.append(temiz_alerjen)

    # 2. Eser Miktar Listesini Kucultme
    urun_eser_miktar = []
    for ham_eser in bulunan_urun["eser_miktar"]:
        temiz_eser = ham_eser.lower()
        urun_eser_miktar.append(temiz_eser)
    
    # Icerik metnini de temizleyerek hazirliyoruz.
    urun_icindekiler_metni = []
    for madde in bulunan_urun["icindekiler"]:
        urun_icindekiler_metni.append(metni_temizle(madde))

    # --- 1. KONTROL: RESMİ ETİKETLER ---
    # Burasi en guvenilir alandir. Eger burada varsa kesinlikle yasaktir.
    for etiket in aranacak_etiketler:
        # in operatoru: "Bu kelime listenin icinde var mi?" diye bakar.
        if etiket in urun_resmi_alerjenler:
            # return kullaniyoruz cunku buldugumuz anda fonksiyonu bitirmeliyiz.
            # Digerlerine bakmaya gerek yok, urun zaten yasakli.
            return {
                "durum": "KIRMIZI",
                "baslik": "YASAK! (Tüketmeyin)",
                "mesaj": f"DİKKAT! Üründe alerjen etiketi bulundu: **'{etiket.upper()}'**\n(Arama: {kullanici_alerjisi})"
            }

    # --- 2. KONTROL: İÇİNDEKİLER METNİ ---
    # Etikette yazmasa bile icindekiler listesinde metin olarak geciyor mu?
    # set() kullaniyoruz: Ayni kelimeleri tekrar tekrar aramayalim diye kumeye ceviriyoruz (Optimizasyon).
    tum_arama_kelimeleri = set(aranacak_etiketler) 
    tum_arama_kelimeleri.add(alerjen_raw) # Kullanicinin orijinal yazdigini da (findik) ekliyoruz.
    
    # Iki katmanli dongu (Nested Loop):
    # Dis dongu: Urunun icerigindeki her maddeyi gezer (un, yag, seker...).
    for madde in urun_icindekiler_metni:
        # Ic dongu: Bizim aradigimiz kelimeleri gezer (hazelnut, nuts, findik).
        for kelime in tum_arama_kelimeleri:
            # in operatoru (Metin ici arama): "fındık" kelimesi "fındık püresi" cumlesinin icinde mi?
            if kelime in madde:
                return {
                    "durum": "KIRMIZI",
                    "baslik": "YASAK! (Tüketmeyin)",
                    "mesaj": f"İçindekiler listesinde tespit edildi: **'{kelime.upper()}'**\n(Madde: {madde})"
                }

    # --- 3. KONTROL: ESER MİKTAR (Risk Analizi) ---
    # "İçerebilir" (May contain) uyarisina bakiyoruz. Burasi KIRMIZI degil TURUNCU alarmdir.
    for etiket in aranacak_etiketler:
        if etiket in urun_eser_miktar:
            return {
                "durum": "TURUNCU",
                "baslik": "RİSKLİ (Eser Miktar)",
                "mesaj": f"Üretim hattından bulaşma riski var: **'{etiket.upper()}'**\n(Pakette 'May contain {etiket}' yazıyor olabilir)"
            }

    # --- SONUÇ: TEMİZ ---
    # Eger kod buraya kadar geldiyse ve hicbir 'return' calismadiysa,
    # demek ki hicbir listede alerjen bulamadik. Urun guvenlidir.
    return {
        "durum": "YESIL",
        "baslik": "GÜVENLİ GÖRÜNÜYOR",
        "mesaj": f"**{marka_adi} - {urun_adi}** analiz edildi.\nArananlar: {', '.join(aranacak_etiketler)}\nTemiz çıktı."
    }

# Bu kisim sadece dosyayi dogrudan calistirirsan devreye girer.
# Baska dosyadan import edince calismaz, boylece guvenli test yapabiliriz.
if __name__ == "__main__":
    print("--- Test Başlıyor ---")
    # Gercek bir barkodla (Nutella) test yapiyoruz.
    print(analiz_et("3017620422003", "Fındık"))