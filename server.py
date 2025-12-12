import socket
import threading
import time
from game_protocol import send_msg, recv_msg

HOST = '0.0.0.0'
PORT = 6000

game_state = {
    "board": [" "] * 9,
    "turn": "X", # İlk sıra X
    "players": [], # (conn, role)
    "game_over": False
}

lock = threading.Lock()

def check_winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    if " " not in board:
        return "DRAW"
    return None

def broadcast_state():
    state = {
        "board": game_state["board"],
        "turn": game_state["turn"],
        "msg": "Oyun devam ediyor..."
    }
    winner = check_winner(game_state["board"])
    
    if winner:
        game_state["game_over"] = True
        state["msg"] = f"OYUN BITTI! Kazanan: {winner}"
        type_msg = "RESULT"
    else:
        type_msg = "STATE"

    for conn, _ in game_state["players"]:
        try:
            send_msg(conn, type_msg, state)
        except: pass

def handle_client(conn, addr):
    print(f"[+] Yeni baglanti: {addr}")
    role = None
    
    with lock:
        if len(game_state["players"]) < 2:
            role = "X" if len(game_state["players"]) == 0 else "O"
            game_state["players"].append((conn, role))
        else:
            conn.close()
            return

    # Handshake
    try:
        msg = recv_msg(conn) # JOIN bekle
        if msg and msg['type'] == 'JOIN':
            send_msg(conn, "WELCOME", {"role": role, "msg": "Bekleniyor..."})
            
            # İkinci oyuncu geldiyse başlat
            if len(game_state["players"]) == 2:
                time.sleep(1)
                for c, r in game_state["players"]:
                     send_msg(c, "START", {"turn": "X"})
    except:
        return

    # Oyun Döngüsü
    while True:
        try:
            msg = recv_msg(conn)
            if not msg: break
            
            if msg['type'] == 'MOVE' and not game_state["game_over"]:
                idx = int(msg['payload']['index'])
                
                with lock:
                    if game_state["turn"] == role and game_state["board"][idx] == " ":
                        # Hamle Yap
                        game_state["board"][idx] = role
                        game_state["turn"] = "O" if role == "X" else "X"
                        broadcast_state()
                    else:
                        send_msg(conn, "ERROR", {"msg": "Siraniz degil veya hatali hamle!"})
                        
        except Exception as e:
            print(f"Hata: {e}")
            break
            
    print(f"[-] Baglanti koptu: {addr}")
    # Basitlik için biri koparsa server kapanabilir veya resetlenebilir
    # conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(2)
    print(f"Server {PORT} portunda açıldı. Oyuncular bekleniyor...")
    
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    start_server()