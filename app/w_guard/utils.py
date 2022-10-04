def is_pub_key(key: str):
    if key.endswith("=") and len(key) == 44:
        return True
    return False
