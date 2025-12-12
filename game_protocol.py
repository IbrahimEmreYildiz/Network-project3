import struct
import json
import socket


# Mesaj gönderirken bu fonksiyonu kullanıyorum.
def send_msg(sock, msg_type, payload={}):
    # Gidecek mesajı json formatına uygun hazırlıyorum.
    message = {
        "ver": 1,
        "type": msg_type,
        "payload": payload
    }
    # Veriyi stringe sonra da byte haline çeviriyorum.
    json_data = json.dumps(message).encode('utf-8')
    # TCP'de veriler birbirine girmesin diye başına uzunluğunu ekliyorum.
    length_prefix = struct.pack('!I', len(json_data))
    sock.sendall(length_prefix + json_data)


# Mesaj alırken de bu fonksiyon işimi görüyor.
def recv_msg(sock):
    try:
        # Önce paketin başındaki 4 byte'lık uzunluk bilgisini okuyorum.
        length_data = recv_all(sock, 4)
        if not length_data: return None
        msg_len = struct.unpack('!I', length_data)[0]

        # O uzunluk kadar veriyi okuyup alıyorum.
        json_data = recv_all(sock, msg_len)
        if not json_data: return None
        # Aldığım veriyi tekrar json yapısına çevirip geri döndürüyorum.
        return json.loads(json_data.decode('utf-8'))
    except:
        return None


# Verinin tamamı gelmeden işlem yapmasın diye bunu yazdım.
def recv_all(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data += packet
    return data