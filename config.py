"""
Uygulama konfigürasyon ayarları.
Hassas bilgiler .env dosyasından yüklenir.
"""
import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import secrets

# .env dosyasını yükle
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Uygulama Ayarları
APP_NAME = os.getenv("APP_NAME", "Ollama Chat")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-here")

# Veritabanı Ayarları
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ollama_chat")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_username")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ollama_chat")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

# Ollama Ayarları
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2")

# Güvenlik Ayarları
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))  # 1 saat
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Dosya İşleme Ayarları
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
ALLOWED_EXTENSIONS = eval(os.getenv("ALLOWED_EXTENSIONS", '["pdf", "docx", "txt", "png", "jpg", "jpeg"]'))

# Klasör oluşturma
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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