import streamlit as st
from datetime import datetime, timedelta
import jwt
from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH, verify_password

def create_jwt_token(username: str) -> str:
    """JWT token oluşturur"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {'sub': username, 'exp': expiration},
        SECRET_KEY,
        algorithm='HS256'
    )

def verify_jwt_token(token: str) -> bool:
    """JWT token doğrular"""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except:
        return False

def login_required(func):
    """Oturum kontrolü için dekoratör"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            show_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper

def is_authenticated() -> bool:
    """Kullanıcının oturum durumunu kontrol eder"""
    return bool(st.session_state.get('authenticated'))

def show_login_page():
    """Giriş sayfasını gösterir"""
    st.title("🔐 Giriş")
    
    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submit = st.form_submit_button("Giriş Yap")
        
        if submit:
            if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.token = create_jwt_token(username)
                st.experimental_rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

def logout():
    """Oturumu kapatır"""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username
    if 'token' in st.session_state:
        del st.session_state.token 