

CEN437 - Network Programming Project 03
Öğrenci Adı: [İbrahim Emre YILDIZ]
Öğrenci No: [2020555069]

========================================================================
BÖLÜM A: Network Araçları (Network Toolkit)
========================================================================

AÇIKLAMA:
Bu bölümde, derste öğrendiğimiz network konularını tek bir menü altında topladım.
Arka planda sürekli çalışan bir "Broadcast Listener" (Dinleyici) ekledim, bu sayede
program hangi menüde olursa olsun gelen duyuruları ekrana basabiliyor.

GEREKLİ KÜTÜPHANELER:
Projeyi çalıştırmadan önce şu kütüphaneleri kurman gerekiyor:
- requests (Web işlemleri için)
- beautifulsoup4 (HTML parçalamak için)

Kurulum komutu:
pip install requests beautifulsoup4

NASIL ÇALIŞTIRILIR:
1. Terminali açın.
2. `python main.py` komutunu yazın.
3. Menüden istediğiniz numarayı seçerek işlem yapabilirsiniz.

MODÜLLERİM:
1. Port Scanner: Girdiğin IP adresindeki açık portları bulur.
2. Device Scanner: Ağdaki diğer cihazları bulmak için ping atar.
3. File Transfer: Basit bir sunucu-istemci mantığıyla dosya transferi yapar.
4. Web Crawler: Bir web sitesindeki linkleri çeker.
5. Wiki Fetcher: Wikipedia'dan özet bilgi getirir.
6. Broadcast: Ağdaki herkese mesaj yollar.

========================================================================
BÖLÜM B: Çok Oyunculu Oyun (Tic-Tac-Toe)
========================================================================

AÇIKLAMA:
Burada TCP üzerinden çalışan kendi oyun protokolümü yazdım. Hazır bir oyun kütüphanesi
kullanmadım. Sunucu (Server) oyunun durumunu yönetiyor, İstemciler (Clients) sadece
bağlanıp hamle yapıyor.

NASIL ÇALIŞTIRILIR:
Bu kısmı test etmek için 3 tane terminal açman lazım:

1. Terminal: `python server.py` yazıp sunucuyu başlat.
2. Terminal: `python client.py` (veya main.py'den 7) yazıp 1. oyuncu ol.
3. Terminal: `python client.py` yazıp 2. oyuncu ol.

İki kişi de bağlanınca oyun otomatik başlıyor.

PROTOKOL ÖZELLİKLERİM (PROTOCOL SPEC):
Oyunun iletişimini şu kurallara göre tasarladım:

- Taşıma Katmanı (Transport): TCP (Veri kaybı olmasın diye)
- Format: JSON (Verileri okuması kolay olsun diye)
- Çerçeveleme (Framing): Length-Prefixed (Uzunluk Önekli)
  (Yani her paketin başına 4 byte uzunluk bilgisi koydum, böylece TCP'de paketler birbirine girmiyor.)

Mesaj Yapısı Şöyle:
{
  "ver": 1,
  "type": "MESAJ_TURU",
  "payload": { ...İçerik... }
}

Kullandığım Mesaj Türleri:
- JOIN: Oyuncu odaya girmek istediğinde gönderiyor.
- WELCOME: Sunucu oyuncuyu kabul edince "Hoşgeldin, rolün X" diyor.
- START: İki kişi de gelince sunucu "Oyun başladı" diyor.
- MOVE: Oyuncu hamle yaptığında (Örn: 4. kutuya koy) gönderiyor.
- STATE: Sunucu her hamleden sonra tahtanın son halini herkese yolluyor.
- RESULT: Oyun bitince (Kazanan/Berabere) sunucu bunu yolluyor.
- ERROR: Hatalı hamle yapılırsa uyarı mesajı.
