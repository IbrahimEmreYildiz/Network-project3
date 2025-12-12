import socket
import threading
import sys
import os
import time
import requests
from bs4 import BeautifulSoup

# --- AYARLAR ---
BROADCAST_PORT = 50000
BROADCAST_IP = '<broadcast>'

# --- 1. BROADCAST LISTENER (ZORUNLU THREAD) ---
def broadcast_listener_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.bind(('', BROADCAST_PORT))
    except:
        return # Sessizce çık

    while True:
        try:
            data, addr = s.recvfrom(1024)
            msg = data.decode('utf-8')
            # Kendi gönderdiğimiz mesajı ekrana basmayalım
            print(f"\n[BROADCAST DUYURU] {addr[0]}: {msg}\n> ", end="") 
        except:
            break

# --- 2. MODÜLLER ---

def port_scanner():
    target = input("Taranacak IP (Örn: 127.0.0.1): ")
    try:
        start_port = int(input("Başlangıç Portu: "))
        end_port = int(input("Bitiş Portu: "))
    except:
        print("Hatalı giriş.")
        return

    print(f"\n--- {target} Taranıyor ---")
    start_time = time.time()
    
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.1) # Hızlı tarama için düşük timeout
        result = s.connect_ex((target, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "Bilinmiyor"
            print(f"[AÇIK] Port {port}: {service}")
        s.close()
    
    print(f"Tarama bitti. Süre: {time.time() - start_time:.2f}sn")

def device_scanner():
    base_ip = input("IP Aralığı (Örn: 192.168.1): ")
    print("Ağ taranıyor (Bu işlem biraz sürebilir)...")
    
    # OS tespiti (Ping komutu farkı için)
    param = '-n' if os.name == 'nt' else '-c'
    
    active_hosts = []
    # Örnek olarak ilk 20 IP'yi tarayalım ki hızlı bitsin (1-20)
    # Tam tarama için range(1, 255) yapabilirsin.
    for i in range(1, 21): 
        ip = f"{base_ip}.{i}"
        response = os.system(f"ping {param} 1 {ip} >nul 2>&1" if os.name=='nt' else f"ping {param} 1 {ip} >/dev/null 2>&1")
        if response == 0:
            print(f"[AKTİF] {ip}")
            active_hosts.append(ip)
            
    print(f"Bulunan cihaz sayısı: {len(active_hosts)}")

def file_transfer():
    print("1. Dosya GÖNDER (Server Modu)")
    print("2. Dosya AL (Client Modu)")
    choice = input("Seçim: ")
    
    if choice == '1':
        # Server Modu
        host = '0.0.0.0'
        port = 9000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)
        print(f"Dosya transfer sunucusu {port} portunda bekleniyor...")
        conn, addr = s.accept()
        print(f"Bağlandı: {addr}")
        
        filename = input("Gönderilecek dosya yolu: ")
        if os.path.exists(filename):
            conn.send(os.path.basename(filename).encode()) # Önce ismi gönder
            time.sleep(0.1)
            with open(filename, 'rb') as f:
                data = f.read(1024)
                while data:
                    conn.send(data)
                    data = f.read(1024)
            print("Dosya gönderildi.")
        else:
            conn.send(b"ERROR")
            print("Dosya bulunamadı.")
        conn.close()
        s.close()
        
    elif choice == '2':
        # Client Modu
        target_ip = input("Gönderici IP: ")
        port = 9000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((target_ip, port))
            filename = s.recv(1024).decode()
            if filename == "ERROR":
                print("Sunucuda dosya yok.")
                return
            
            print(f"{filename} indiriliyor...")
            with open(f"downloaded_{filename}", 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data: break
                    f.write(data)
            print("Transfer tamamlandı.")
        except Exception as e:
            print(f"Hata: {e}")
        finally:
            s.close()

def web_crawler():
    url = input("URL girin (http:// ile): ")
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"\n--- {url} Linkleri ---")
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('http'):
                print(href)
    except Exception as e:
        print(f"Hata: {e}")

def wiki_fetcher():
    topic = input("Wikipedia'da ne arayalım?: ")
    try:
        # Wikipedia API kullanımı
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}")
        if resp.status_code == 200:
            data = resp.json()
            print("\n--- ÖZET ---")
            print(data.get('extract', 'Özet bulunamadı.'))
        else:
            print("Konu bulunamadı.")
    except Exception as e:
        print(f"Hata: {e}")

def send_broadcast_msg():
    msg = input("Yayınlanacak Mesaj: ")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg.encode(), (BROADCAST_IP, BROADCAST_PORT))
    print("Mesaj gönderildi.")

# --- MENÜ ---
def main():
    # Arka plan thread başlat
    t = threading.Thread(target=broadcast_listener_thread, daemon=True)
    t.start()
    
    while True:
        print("\n=== NETWORK PROJECT (PART A) ===")
        print("1. Port Scanner")
        print("2. Network Device Scanner")
        print("3. File Transfer")
        print("4. Web Crawler")
        print("5. Wikipedia Fetcher")
        print("6. Broadcast Mesaj Gönder")
        print("7. Çıkış")
        
        c = input("Seçiminiz: ")
        
        if c == '1': port_scanner()
        elif c == '2': device_scanner()
        elif c == '3': file_transfer()
        elif c == '4': web_crawler()
        elif c == '5': wiki_fetcher()
        elif c == '6': send_broadcast_msg()
        elif c == '7': sys.exit()
        else: print("Geçersiz seçim.")

if __name__ == "__main__":
    main()