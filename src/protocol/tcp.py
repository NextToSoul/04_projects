import socket
import threading
from src.protocol.base import ProtocolDriver

class TcpDriver(ProtocolDriver):
    def __init__(self):
        self._sock = None
        self._host = '127.0.0.1'
        self._port = 20004
        self._timeout = 5.0
        self._reconnect = False
        self._reconnect_interval = 2.0
        self._recv_callback = None
        self._running = False
        self._connected = False
        self._recv_thread = None
        self._lock = threading.Lock()

    def open(self, config: dict) -> bool:
        self._host = config.get('host', self._host)
        self._port = config.get('port', self._port)
        self._timeout = config.get('timeout', self._timeout)
        self._reconnect = config.get('reconnect', self._reconnect)
        self._reconnect_interval = config.get('reconnect_interval', self._reconnect_interval)
        return self._connect()

    def _connect(self) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect((self._host, self._port))
            self._sock = sock
            self._connected = True
            self._running = True
            self._start_receive_thread()
            return True
        except Exception:
            self._sock = None
            self._connected = False
            return False

    def close(self):
        self._running = False
        self._connected = False
        if self._recv_thread:
            self._recv_thread.join(timeout=1.0)
        with self._lock:
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
                self._sock = None

    def send(self, data: bytes):
        if not self._connected or not self._sock:
            raise ConnectionError('Not connected to ' + self._host + ':' + str(self._port))
        with self._lock:
            self._sock.sendall(data)

    def set_receive_callback(self, callback):
        self._recv_callback = callback

    def is_open(self) -> bool:
        return self._connected and self._sock is not None

    @property
    def name(self) -> str:
        return 'tcp://' + self._host + ':' + str(self._port)

    def _start_receive_thread(self):
        def _recv_loop():
            while self._running and self._connected:
                try:
                    data = self._sock.recv(4096)
                    if not data:
                        self._connected = False
                        break
                    if self._recv_callback:
                        self._recv_callback(data)
                except socket.timeout:
                    continue
                except Exception:
                    self._connected = False
                    break
        self._recv_thread = threading.Thread(target=_recv_loop, daemon=True)
        self._recv_thread.start()
