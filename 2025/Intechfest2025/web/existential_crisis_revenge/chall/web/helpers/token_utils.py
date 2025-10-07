import os

allowedTab = {}

def get_random_bytes(length: int) -> bytes:
    return os.urandom(length)

def get_random_hex(size: int = 3) -> str:
    return get_random_bytes(size).hex()
    
if __name__ == "__main__":
    print(get_random_hex())