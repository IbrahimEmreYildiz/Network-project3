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

    # Windows mu Linux mu ona göre ping komutu değişiyor, onu ayarladım.
    param = '-n' if os.name == 'nt' else '-c'

    active_hosts = []
    # Hepsini tararsam çok uzun sürüyor o yüzden ilk 20 tanesine bakıyorum.
    for i in range(1, 21):
        ip = f"{base_ip}.{i}"
        # Ping atıyorum cevap gelirse cihaz aktiftir.
        response = os.system(
            f"ping {param} 1 {ip} >nul 2>&1" if os.name == 'nt' else f"ping {param} 1 {ip} >/dev/null 2>&1")
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