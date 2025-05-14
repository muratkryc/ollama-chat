import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import secrets

# .env dosyasını yükle
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Veritabanı ayarları
DB_CONFIG = {
    'host': os.getenv('PGHOST', 'ep-fragrant-tree-a45mz980-pooler.us-east-1.aws.neon.tech'),
    'database': os.getenv('PGDATABASE', 'ollama'),
    'user': os.getenv('PGUSER', 'ollama_owner'),
    'password': os.getenv('PGPASSWORD', 'npg_VrZLz6C0wibm')
}

# Güvenlik ayarları
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFyXjs2gn8hQe9i')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifre doğrulama fonksiyonu"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Şifre hash'leme fonksiyonu"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8') 