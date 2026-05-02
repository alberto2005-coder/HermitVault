import socket
import json
import threading
import os

class SyncManager:
    def __init__(self, port=5555):
        self.port = port
        self.running = False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_server(self, vault_path, on_success):
        """Starts a temporary server to send the vault file."""
        def run():
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('', self.port))
                server.listen(1)
                server.settimeout(60) # Timeout after 1 min
                
                self.running = True
                conn, addr = server.accept()
                
                with open(vault_path, "rb") as f:
                    data = f.read()
                    # Send size first
                    conn.sendall(len(data).to_bytes(4, 'big'))
                    # Send data
                    conn.sendall(data)
                
                conn.close()
                server.close()
                on_success(f"Sent vault to {addr[0]}")
            except Exception as e:
                on_success(f"Error: {e}")
            finally:
                self.running = False

        threading.Thread(target=run, daemon=True).start()

    def receive_vault(self, target_ip, on_data):
        """Connects to a server to receive the vault file."""
        def run():
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((target_ip, self.port))
                
                # Receive size
                size_data = client.recv(4)
                size = int.from_bytes(size_data, 'big')
                
                # Receive vault
                data = b""
                while len(data) < size:
                    chunk = client.recv(min(size - len(data), 4096))
                    if not chunk: break
                    data += chunk
                
                client.close()
                on_data(data)
            except Exception as e:
                on_data(f"Error: {e}")

        threading.Thread(target=run, daemon=True).start()
