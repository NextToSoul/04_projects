from src.protocol.tcp import TcpDriver

DRIVER_REGISTRY = {}

def register_driver(name, driver_class):
    DRIVER_REGISTRY[name] = driver_class

def get_driver(name):
    if name not in DRIVER_REGISTRY:
        raise KeyError('Driver not registered: ' + name)
    return DRIVER_REGISTRY[name]()

register_driver('tcp', TcpDriver)
