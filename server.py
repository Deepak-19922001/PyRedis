import socket
import threading

from protocol import process_command


class Server:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        if not all(hasattr(self, attr) for attr in ['host', 'port', 'db']):
            print("FATAL: Server object not initialized correctly.")
            return

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"PyRedis server listening on {self.host}:{self.port}...")
            print("Connect with `telnet` or a Redis client.")

            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"INFO: Accepted connection from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, self.db)
                )
                client_thread.daemon = True
                client_thread.start()

        except OSError as e:
            print(f"FATAL: Could not bind to {self.host}:{self.port}. Error: {e}")
            self.shutdown()
        except KeyboardInterrupt:
            print("\nINFO: Shutdown signal received.")

    def handle_client(self, client_socket, db):
        try:
            while True:
                request_bytes = client_socket.recv(1024)
                if not request_bytes:
                    break

                request_str = request_bytes.decode('utf-8').strip()
                response_bytes = process_command(request_str, db)

                if response_bytes == b"QUIT":
                    break

                if response_bytes:
                    client_socket.sendall(response_bytes)

        except ConnectionResetError:
            print("INFO: Client disconnected abruptly.")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred in client handler: {e}")
        finally:
            print("INFO: Client connection closed.")
            client_socket.close()

    def shutdown(self):
        print("INFO: Shutting down server.")
        self.server_socket.close()