import socket
import json
import threading
import os

class SyncManager:
    def __init__(self, port=5555):
        self.port = port
        self.running = False
        self.server_sock = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_server(self, vault_path, pin, on_success, port=None):
        """Starts a temporary server to send the vault file with numeric PIN handshake."""
        if port: self.port = int(port)
        if self.running: return
        
        def run():
            try:
                self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_sock.bind(('', self.port))
                self.server_sock.listen(1)
                self.server_sock.settimeout(60) # Timeout after 1 min
                
                self.running = True
                conn, addr = self.server_sock.accept()
                
                # Receive pairing PIN (6 bytes)
                received_pin_data = conn.recv(6)
                if not received_pin_data:
                    conn.close()
                    raise Exception("Connection closed before sending pairing PIN")
                
                received_pin = received_pin_data.decode('utf-8', errors='ignore')
                if received_pin != pin:
                    conn.close()
                    raise Exception(f"Unauthorized connection attempt from {addr[0]} (invalid PIN)")
                
                with open(vault_path, "rb") as f:
                    data = f.read()
                    # Send size first
                    conn.sendall(len(data).to_bytes(4, 'big'))
                    # Send data
                    conn.sendall(data)
                
                conn.close()
                self.server_sock.close()
                on_success(f"Sent vault to {addr[0]}")
            except socket.timeout:
                on_success("Hosting timed out (no connection received)")
            except Exception as e:
                if self.running: # Only report if not manually stopped
                    on_success(f"Error: {e}")
            finally:
                self.running = False
                if self.server_sock:
                    try: self.server_sock.close()
                    except: pass
                self.server_sock = None

        threading.Thread(target=run, daemon=True).start()

    def stop_server(self):
        self.running = False
        if self.server_sock:
            try:
                # Force close the socket to break the accept() or timeout
                self.server_sock.close()
            except:
                pass
            self.server_sock = None
        return True

    def receive_vault(self, target_ip, pin, on_data, port=None):
        """Connects to a server to receive the vault file after performing PIN handshake."""
        if port: self.port = port
        def run():
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(15) # 15 second timeout for sync operations
                client.connect((target_ip, self.port))
                
                # Send pairing PIN (6 bytes)
                client.sendall(pin.encode('utf-8'))
                
                # Receive size
                size_data = client.recv(4)
                if not size_data:
                    raise Exception("No data received from host (possibly incorrect PIN)")
                
                size = int.from_bytes(size_data, 'big')
                
                # Limit size to prevent OOM/DoS (max 50 MB)
                MAX_VAULT_SIZE = 50 * 1024 * 1024
                if size > MAX_VAULT_SIZE:
                    raise ValueError(f"Vault size {size} bytes exceeds maximum safety limit (50MB)")
                
                # Receive vault
                data = b""
                while len(data) < size:
                    chunk = client.recv(min(size - len(data), 4096))
                    if not chunk: break
                    data += chunk
                
                client.close()
                if len(data) < size:
                    raise Exception("Connection closed before entire vault file was received")
                on_data(data)
            except Exception as e:
                on_data(f"Error: {e}")

        threading.Thread(target=run, daemon=True).start()
