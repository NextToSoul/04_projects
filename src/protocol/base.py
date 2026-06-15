from abc import ABC, abstractmethod

class ProtocolDriver(ABC):
    @abstractmethod
    def open(self, config: dict) -> bool:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def set_receive_callback(self, callback):
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
