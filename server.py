import socket
import threading
import time
from game_protocol import send_msg, recv_msg

HOST = '0.0.0.0'
PORT = 6000

# Oyunun bütün durumunu burada tutuyorum, kimin sırası, tahta ne durumda vs.
game_state = {
    "board": [" "] * 9,
    "turn": "X",  # İlk X başlasın dedim.
    "players": [],  # Bağlı oyuncuları buraya ekliyorum.
    "game_over": False
}

# Aynı anda iki kişi işlem yaparsa karışıklık olmasın diye kilit koydum.
lock = threading.Lock()


# Kim kazandı diye kontrol ettiğim yer burası.
def check_winner(board):
    wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    if " " not in board:
        return "DRAW"  # Yer kalmadıysa berabere bitiriyorum.
    return None


# Her hamleden sonra son durumu herkese haber veriyorum.
def broadcast_state():
    state = {
        "board": game_state["board"],
        "turn": game_state["turn"],
        "msg": "Oyun devam ediyor..."
    }
    winner = check_winner(game_state["board"])

    if winner:
        game_state["game_over"] = True
        state["msg"] = f"OYUN BİTTİ! Kazanan: {winner}"
        type_msg = "RESULT"
    else:
        type_msg = "STATE"

    # Bağlı herkese tek tek gönderiyorum.
    for conn, _ in game_state["players"]:
        try:
            send_msg(conn, type_msg, state)
        except:
            pass


def handle_client(conn, addr):
    print(f"[+] Biri bağlandı: {addr}")
    role = None

    with lock:
        # İki kişiden fazla olmasın diye kontrol ediyorum.
        if len(game_state["players"]) < 2:
            role = "X" if len(game_state["players"]) == 0 else "O"
            game_state["players"].append((conn, role))
        else:
            conn.close()
            return

    # Giriş işlemleri burada.
    try:
        msg = recv_msg(conn)  # Oyuncunun katılma isteğini bekliyorum.
        if msg and msg['type'] == 'JOIN':
            send_msg(conn, "WELCOME", {"role": role, "msg": "Rakip bekleniyor..."})

            # İkinci kişi de geldiyse oyunu başlatıyorum.
            if len(game_state["players"]) == 2:
                time.sleep(1)
                for c, r in game_state["players"]:
                    send_msg(c, "START", {"turn": "X"})

                # Tahtayı herkese gönderiyorum ki oyun başlasın.
                broadcast_state()

    except:
        return

    # Oyun burada dönüyor.
    while True:
        try:
            msg = recv_msg(conn)
            if not msg: break

            # Hamle geldiyse ve oyun bitmediyse bakıyorum.
            if msg['type'] == 'MOVE' and not game_state["game_over"]:
                try:
                    idx = int(msg['payload']['index'])
                except:
                    continue

                with lock:
                    # Hamle geçerli mi, sıra onda mı ve o kare boş mu diye bakıyorum.
                    if game_state["turn"] == role and game_state["board"][idx] == " ":
                        # Hamleyi işliyorum.
                        game_state["board"][idx] = role
                        game_state["turn"] = "O" if role == "X" else "X"
                        broadcast_state()  # Yeni durumu herkese yayıyorum.
                    else:
                        send_msg(conn, "ERROR", {"msg": "Sıra sende değil veya orası dolu!"})

        except Exception as e:
            print(f"Hata oldu: {e}")
            break

    print(f"[-] Bağlantı koptu: {addr}")


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
    except OSError:
        print(f"HATA: {PORT} portu dolu, önceki terminali kapatmayı unuttun herhalde.")
        return

    s.listen(2)
    print(f"Server {PORT} portunda açıldı, oyuncuları bekliyorum.")

    while True:
        conn, addr = s.accept()
        # Her oyuncu için ayrı bir iş parçacığı açıyorum.
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()


if __name__ == "__main__":
    start_server()