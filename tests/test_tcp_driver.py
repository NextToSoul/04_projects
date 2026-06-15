import socket
import pytest
from unittest.mock import patch, MagicMock
from src.protocol.tcp import TcpDriver
from src.protocol.registry import get_driver, register_driver


@pytest.fixture
def mock_conn():
    with patch('socket.socket') as mock_sock:
        instance = MagicMock()
        instance.recv.side_effect = socket.timeout
        mock_sock.return_value = instance
        driver = TcpDriver()
        driver.open({'host': '127.0.0.1', 'port': 20004})
        yield driver, instance
        driver.close()


def test_connect_success():
    with patch('socket.socket') as mock_sock:
        instance = MagicMock()
        instance.recv.side_effect = socket.timeout
        mock_sock.return_value = instance
        driver = TcpDriver()
        result = driver.open({'host': '192.168.117.26', 'port': 20004})
        assert result is True
        assert driver.is_open() is True
        assert '192.168.117.26' in driver.name
        driver.close()


def test_connect_error():
    with patch('socket.socket') as mock_sock:
        mock_sock.side_effect = Exception('Connection refused')
        driver = TcpDriver()
        result = driver.open({'host': '192.168.117.26', 'port': 20004})
        assert result is False
        assert driver.is_open() is False


def test_send_data(mock_conn):
    driver, instance = mock_conn
    driver.send(b'\xeb\x90\x00\x1a')
    instance.sendall.assert_called_once_with(b'\xeb\x90\x00\x1a')


def test_send_error():
    with patch('socket.socket') as mock_sock:
        instance = MagicMock()
        instance.recv.side_effect = socket.timeout
        mock_sock.return_value = instance
        driver = TcpDriver()
        driver.open({'host': '127.0.0.1', 'port': 20004})
        driver.close()
        with pytest.raises(ConnectionError):
            driver.send(b'\x00')


def test_close(mock_conn):
    driver, instance = mock_conn
    assert driver.is_open() is True
    driver.close()
    assert driver.is_open() is False


def test_name():
    driver = TcpDriver()
    driver.open({'host': '192.168.117.26', 'port': 20004})
    assert driver.name == 'tcp://192.168.117.26:20004'
    driver.close()


def test_receive_callback():
    with patch('socket.socket') as mock_sock:
        instance = MagicMock()
        instance.recv.side_effect = [b'\x1a\xcf\x05\x25', socket.timeout]
        mock_sock.return_value = instance
        received = []
        driver = TcpDriver()
        driver.set_receive_callback(lambda d: received.append(d))
        driver.open({'host': '127.0.0.1', 'port': 20004})
        import time
        time.sleep(0.05)
        assert len(received) == 1
        assert received[0] == b'\x1a\xcf\x05\x25'
        driver.close()


def test_default_config():
    driver = TcpDriver()
    assert '127.0.0.1' in driver.name
    assert '20004' in driver.name


def test_registry_get_tcp():
    driver = get_driver('tcp')
    assert isinstance(driver, TcpDriver)


def test_registry_custom():
    class MockDriver:
        pass
    register_driver('test_mock', MockDriver)
    d = get_driver('test_mock')
    assert isinstance(d, MockDriver)
