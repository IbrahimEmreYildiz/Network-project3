import socket
import threading
import sys
import os
import time
import requests
from bs4 import BeautifulSoup

# Yayını yapacağım portu ve adresi burada belirledim.
BROADCAST_PORT = 50000
BROADCAST_IP = '<broadcast>'


# BURASI ARKA PLAN DİNLEYİCİSİ
def broadcast_listener_thread():
    # Broadcast için UDP lazım, o yüzden UDP soketi açtım.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        # Portu dinlemeye başlıyorum.
        s.bind(('', BROADCAST_PORT))
    except:
        # Eğer port doluysa hata verip programı çökertmesin, sessizce çıksın.
        return

    while True:
        try:
            # Sürekli gelen mesaj var mı diye bakıyorum.
            data, addr = s.recvfrom(1024)
            msg = data.decode('utf-8')
            # Ekrana basarken karışıklık olmasın diye formatladım.
            print(f"\n[BROADCAST DUYURU] {addr[0]}: {msg}\n> ", end="")
        except:
            break


# BURADAN SONRASI MODÜLLER

def port_scanner():
    target = input("Taranacak IP (Örn: 127.0.0.1): ")
    try:
        # Hangi aralığı tarayacağımızı soruyorum.
        start_port = int(input("Başlangıç Portu: "))
        end_port = int(input("Bitiş Portu: "))
    except:
        print("Sayı girmedin sanırım hatalı oldu.")
        return

    print(f"\n {target} adresi taranıyor biraz bekle...")
    start_time = time.time()

    # Tek tek portları dolaşıyorum.
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Hızlı olsun diye timeout süresini kısa tuttum yoksa çok bekletiyor.
        socket.setdefaulttimeout(0.1)
        result = s.connect_ex((target, port))
        if result == 0:
            try:
                # Port açıksa ne olduğunu anlamaya çalışıyorum.
                service = socket.getservbyport(port)
            except:
                service = "Bilinmiyor"
            print(f"[AÇIK] Port {port}: {service}")
        s.close()

    print(f"Tarama bitti, şu kadar sürdü: {time.time() - start_time:.2f} saniye")


def device_scanner():
    base_ip = input("IP Aralığı (Örn: 192.168.1): ")
    print("Ağı tarıyorum, biraz uzun sürebilir bu iş...")


    if os.name == 'nt':
        ping_cmd = r"C:\Windows\System32\ping.exe"
        param = '-n'
        redirect = ""
    else:
        ping_cmd = "ping"
        param = '-c'
        redirect = ">/dev/null 2>&1"

    active_hosts = []
    # Tarama uzun sürmesin diye sadece ilk 10 IP'ye bakalım
    for i in range(1, 11):
        ip = f"{base_ip}.{i}"

        # Komutu oluşturuyorum
        if os.name == 'nt':
            # Windows için özel komut yapısı
            command = f'"{ping_cmd}" {param} 1 {ip} >nul 2>&1'
        else:
            command = f"{ping_cmd} {param} 1 {ip} {redirect}"

        response = os.system(command)

        if response == 0:
            print(f"[AKTİF] {ip}")
            active_hosts.append(ip)

    print(f"Toplam {len(active_hosts)} tane cihaz buldum.")


def file_transfer():
    print("1. Dosya GÖNDER (Server Modu)")
    print("2. Dosya AL (Client Modu)")
    choice = input("Seçiminiz: ")

    if choice == '1':
        # Dosya gönderen taraf sunucu gibi davranıyor.
        host = '0.0.0.0'
        port = 9000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)
        print(f"Dosya atmak için {port} portunu açtım bekliyorum.")
        conn, addr = s.accept()
        print(f"{addr} bağlandı, şimdi dosyayı atacağım.")

        filename = input("Dosyanın yolunu yaz: ")
        if os.path.exists(filename):
            # Önce dosyanın adını yolluyorum ki karşı taraf ne geldiğini bilsin.
            conn.send(os.path.basename(filename).encode())
            time.sleep(0.1)
            # Dosyayı parça parça okuyup karşı tarafa postalıyorum.
            with open(filename, 'rb') as f:
                data = f.read(1024)
                while data:
                    conn.send(data)
                    data = f.read(1024)
            print("Dosyayı yolladım, bitti.")
        else:
            conn.send(b"ERROR")
            print("Böyle bir dosya yok ki.")
        conn.close()
        s.close()

    elif choice == '2':
        # Dosya alan taraf istemci oluyor.
        target_ip = input("Gönderici IP: ")
        port = 9000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((target_ip, port))
            # İlk gelen veri dosya ismi, onu alıyorum.
            filename = s.recv(1024).decode()
            if filename == "ERROR":
                print("Karşı tarafta dosya yokmuş.")
                return

            print(f"{filename} iniyor şu an...")
            # Gelen veriyi yeni dosyaya yazıyorum.
            with open(f"downloaded_{filename}", 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data: break
                    f.write(data)
            print("İndirme işlemi tamam.")
        except Exception as e:
            print(f"Bir aksilik oldu: {e}")
        finally:
            s.close()


def web_crawler():
    url = input("Hangi sitenin linklerini çekelim (http:// ile başla): ")
    try:
        # Sayfaya istek atıp içeriğini alıyorum.
        resp = requests.get(url, timeout=5)
        # HTML kodlarını parçalamak için bu kütüphaneyi kullandım.
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"\n {url} içindeki linkler şöyle:")
        for link in soup.find_all('a'):
            href = link.get('href')
            # Sadece http ile başlayan gerçek linkleri gösteriyorum.
            if href and href.startswith('http'):
                print(href)
    except Exception as e:
        print(f"Hata çıktı: {e}")


def wiki_fetcher():
    topic = input("Wikipedia'da ne arayalım: ")
    try:
        # Wikipedia'nın hazır API'sine bağlanıp özet çekiyorum.
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}")
        if resp.status_code == 200:
            data = resp.json()
            print("\n ÖZET BİLGİ ")
            print(data.get('extract', 'Özet bulamadım.'))
        else:
            print("Aradığın şey yok galiba.")
    except Exception as e:
        print(f"Bağlantı hatası var: {e}")


def send_broadcast_msg():
    msg = input("Herkese ne söylemek istersin: ")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Broadcast izni vermezsem göndermiyor, o yüzden bunu açtım.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg.encode(), (BROADCAST_IP, BROADCAST_PORT))
    print("Mesajı herkese yaydım.")


def start_game_client():
    print("\n OYUN İSTEMCİSİ AÇILIYOR ")
    print("Unutma önce server.py dosyasını çalıştırman lazım yoksa bağlanmaz.")
    # İşletim sistemine göre doğru komutu veriyorum.
    cmd = 'python client.py' if os.name == 'nt' else 'python3 client.py'
    os.system(cmd)


# ANA MENÜ KISMI
def main():
    # Program başlar başlamaz arka planda dinleyiciyi başlatıyorum ki mesajları kaçırmayalım.
    t = threading.Thread(target=broadcast_listener_thread, daemon=True)
    t.start()

    while True:
        print("\n NETWORK PROJECT ANA MENÜ ")
        print(" PART A ARAÇLAR ")
        print("1. Port Scanner")
        print("2. Network Device Scanner")
        print("3. File Transfer")
        print("4. Web Crawler")
        print("5. Wikipedia Fetcher")
        print("6. Broadcast Mesaj Gönder")
        print(" PART B OYUN ")
        print("7. Tic-Tac-Toe Oyna (Client Başlat)")
        print("8. Çıkış")

        c = input("Seçiminiz: ")

        # Seçime göre ilgili fonksiyonu çağırıyorum.
        if c == '1':
            port_scanner()
        elif c == '2':
            device_scanner()
        elif c == '3':
            file_transfer()
        elif c == '4':
            web_crawler()
        elif c == '5':
            wiki_fetcher()
        elif c == '6':
            send_broadcast_msg()
        elif c == '7':
            start_game_client()
        elif c == '8':
            sys.exit()
        else:
            print("Yanlış tuşladın galiba.")


# --- İŞTE BU KISIM EKSİK OLDUĞU İÇİN ÇALIŞMIYORDU ---
if __name__ == "__main__":
    main()