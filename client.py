import socket
import threading
import sys
from game_protocol import send_msg, recv_msg


# Tahtayı ekrana düzgünce çizdirmek için bunu yazdım.
def print_board(board):
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")


# Oyunun ana döngüsü burada, sürekli sunucuyu dinliyorum.
def game_loop(sock, my_role):
    while True:
        msg = recv_msg(sock)
        if not msg: break

        m_type = msg['type']
        payload = msg['payload']

        if m_type == 'START':
            print(f"\n OYUN BAŞLADI ")
            print(f"Sıra: {payload['turn']}")

        elif m_type == 'STATE':
            # Güncel tahtayı ekrana basıyorum.
            print_board(payload['board'])
            print(f"Sıra: {payload['turn']}")
            if payload['turn'] == my_role:
                # Sıra bendeyse benden hamle istiyor.
                move = input(f"Sizin sıranız ({my_role}) [0-8]: ")
                send_msg(sock, "MOVE", {"index": int(move)})
            else:
                print("Rakibin oynamasını bekliyorum...")

        elif m_type == 'RESULT':
            print_board(payload['board'])
            print(f"OYUN BİTTİ! {payload['msg']}")
            break

        elif m_type == 'ERROR':
            print(f"[UYARI] {payload['msg']}")


def main():
    ip = input("Sunucu IP (Localhost için Enter'a bas): ")
    if not ip: ip = '127.0.0.1'
    port = 6000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
    except:
        print("Sunucuya bağlanamadım, sunucuyu açtığından emin misin?")
        return

    # Oyuna girmek istediğimi söylüyorum.
    send_msg(s, "JOIN", {})

    # Sunucudan cevap bekliyorum.
    resp = recv_msg(s)
    if resp and resp['type'] == 'WELCOME':
        my_role = resp['payload']['role']
        print(f"Sunucuya bağlandım. Rolüm: {my_role}")
        print(resp['payload']['msg'])

        # Her şey tamamsa oyun başlasın.
        game_loop(s, my_role)
    else:
        print("Bağlantı reddedildi.")

    s.close()


if __name__ == "__main__":
    main()