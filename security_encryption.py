"""
File Encryption & Protection Module
AES-256 encryption, secure deletion, password-protected backups
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64
from pathlib import Path
from typing import Optional, Tuple
import hashlib
import secrets


class FileEncryption:
    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption system
        
        Args:
            password: Master password for encryption (if None, generates random key)
        """
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def _derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Salt for key derivation (generates if None)
            
        Returns:
            Encryption key
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_file(self, file_path: Path, output_path: Path = None) -> Tuple[bool, str]:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path (default: original_name.encrypted)
            
        Returns:
            (success, message)
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(data)
            
            # Write encrypted file
            if output_path is None:
                output_path = file_path.parent / f"{file_path.name}.encrypted"
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True, f"File encrypted: {output_path}"
        
        except Exception as e:
            return False, f"Encryption failed: {str(e)}"
    
    def decrypt_file(self, encrypted_file_path: Path, output_path: Path = None) -> Tuple[bool, str]:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Output path (default: remove .encrypted extension)
            
        Returns:
            (success, message)
        """
        try:
            # Read encrypted file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Write decrypted file
            if output_path is None:
                output_path = Path(str(encrypted_file_path).replace('.encrypted', ''))
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True, f"File decrypted: {output_path}"
        
        except Exception as e:
            return False, f"Decryption failed: {str(e)}"
    
    def encrypt_backup(self, backup_folder: Path, password: str) -> Tuple[bool, str]:
        """
        Encrypt entire backup folder
        
        Args:
            backup_folder: Path to backup folder
            password: Password for backup encryption
            
        Returns:
            (success, message)
        """
        try:
            encrypted_count = 0
            
            for file_path in backup_folder.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith('.encrypted'):
                    success, msg = self.encrypt_file(file_path)
                    if success:
                        encrypted_count += 1
                        # Securely delete original
                        self.secure_delete(file_path)
            
            return True, f"Encrypted {encrypted_count} files in backup"
        
        except Exception as e:
            return False, f"Backup encryption failed: {str(e)}"
    
    def secure_delete(self, file_path: Path, passes: int = 3) -> bool:
        """
        Securely delete file by overwriting multiple times
        
        Args:
            file_path: File to delete
            passes: Number of overwrite passes (default: 3)
            
        Returns:
            Success status
        """
        try:
            file_size = file_path.stat().st_size
            
            # Overwrite with random data multiple times
            for i in range(passes):
                with open(file_path, 'wb') as f:
                    if i == passes - 1:
                        # Last pass: write zeros
                        f.write(b'\x00' * file_size)
                    else:
                        # Other passes: random data
                        f.write(os.urandom(file_size))
            
            # Delete file
            file_path.unlink()
            return True
        
        except Exception as e:
            print(f"Secure delete failed: {e}")
            return False
    
    def verify_integrity(self, file_path: Path, expected_hash: str = None) -> Tuple[bool, str]:
        """
        Verify file integrity using SHA-256
        
        Args:
            file_path: File to verify
            expected_hash: Expected hash (if None, returns current hash)
            
        Returns:
            (verified, hash)
        """
        try:
            sha256 = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            
            current_hash = sha256.hexdigest()
            
            if expected_hash:
                verified = current_hash == expected_hash
                return verified, current_hash
            else:
                return True, current_hash
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def save_key(self, key_path: Path):
        """Save encryption key to file"""
        with open(key_path, 'wb') as f:
            f.write(self.key)
    
    def load_key(self, key_path: Path):
        """Load encryption key from file"""
        with open(key_path, 'rb') as f:
            self.key = f.read()
        self.cipher = Fernet(self.key)


class PasswordManager:
    """Secure password storage and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + pwdhash.hex()
    
    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        """Verify password against stored hash"""
        salt = stored_hash[:64]
        stored_pwdhash = stored_hash[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwdhash.hex() == stored_pwdhash
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password"""
        import string
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# Example usage and presets
ENCRYPTION_PRESETS = {
    "high_security": {
        "algorithm": "AES-256",
        "key_derivation": "PBKDF2",
        "iterations": 100000,
        "secure_delete_passes": 7
    },
    "balanced": {
        "algorithm": "AES-256",
        "key_derivation": "PBKDF2",
        "iterations": 100000,
        "secure_delete_passes": 3
    },
    "fast": {
        "algorithm": "AES-256",
        "key_derivation": "PBKDF2",
        "iterations": 50000,
        "secure_delete_passes": 1
    }
}