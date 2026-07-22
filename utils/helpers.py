import random
from datetime import datetime

def rand_ip():
    return f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def rand_port():
    return random.randint(1024, 65535)

def ts():
    return datetime.now().strftime("%H:%M:%S")

def dt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
