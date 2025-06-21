# ds-rpc-02/app/utils/security.py

import hashlib
import os

class SecurityManager:
    def hash_password(self, password: str) -> str:
        # Hash password with salt
        salt = os.urandom(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + hashed.hex()

    def verify_password(self, password: str, stored_hash: str) -> bool:
        # Extract salt and hash
        salt_hex = stored_hash[:32]
        hash_hex = stored_hash[32:]
        salt = bytes.fromhex(salt_hex)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
        return hashed == hash_hex
    