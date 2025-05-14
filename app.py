import streamlit as st
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.base import BaseCallbackHandler
import json
import requests
import tempfile
import os
from PIL import Image
import pytesseract
import magic
import docx
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from auth import login_required, show_login_page, logout, is_authenticated
from database import init_db, save_conversation, save_message, save_file_content, get_conversation_history, search_similar_content

# Veritabanını başlat
init_db()

# Desteklenen dosya tipleri
ALLOWED_EXTENSIONS = {
    'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    'document': ['.pdf', '.doc', '.docx', '.txt']
}

def get_file_type(file):
    """
    Yüklenen dosyanın tipini belirler
    """
    mime = magic.Magic()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.getvalue())
        file_type = mime.from_file(temp_file.name)
        os.unlink(temp_file.name)
    return file_type

def extract_text_from_image(image_path):
    """
    Görselden metin çıkarma
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='tur+eng')
        return text.strip()
    except Exception as e:
        st.error(f"Görsel işleme hatası: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    PDF dosyasından metin çıkarma
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Eğer PDF'den metin çıkarılamazsa OCR dene
        if not text.strip():
            images = convert_from_path(pdf_path)
            for image in images:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                    image.save(temp_img.name)
                    text += extract_text_from_image(temp_img.name) + "\n"
                    os.unlink(temp_img.name)
        return text.strip()
    except Exception as e:
        st.error(f"PDF işleme hatası: {str(e)}")
        return ""

def extract_text_from_docx(docx_path):
    """
    Word dosyasından metin çıkarma
    """
    try:
        doc = docx.Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Word dosyası işleme hatası: {str(e)}")
        return ""

def process_uploaded_file(uploaded_file):
    """
    Yüklenen dosyayı işler ve metin çıkarır
    """
    if uploaded_file is None:
        return ""
    
    try:
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            file_path = temp_file.name
        
        # Dosya tipine göre işle
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext in ALLOWED_EXTENSIONS['image']:
            text = extract_text_from_image(file_path)
        elif file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            text = extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            text = uploaded_file.getvalue().decode('utf-8')
        else:
            text = ""
            st.warning("Desteklenmeyen dosya formatı")
        
        # Geçici dosyayı sil
        os.unlink(file_path)
        return text
    
    except Exception as e:
        st.error(f"Dosya işleme hatası: {str(e)}")
        return ""

# Callback handler for streaming
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        
    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text + "▌")

# Sayfa yapılandırması
st.set_page_config(
    page_title="Ollama Chat",
    page_icon="💬",
    layout="wide"
)

# Oturum kontrolü
if not is_authenticated():
    show_login_page()
else:
    # Başlık ve açıklama
    st.title("💬 Ollama Chat")
    st.caption("Yerel Ollama modelleriyle sohbet edin")
    
    # Çıkış butonu
    if st.sidebar.button("🚪 Çıkış Yap"):
        logout()
        st.experimental_rerun()
    
    # Yan menü ayarları
    with st.sidebar:
        st.title("⚙️ Ayarlar")
        
        # Dosya yükleme bölümü
        st.subheader("📎 Dosya Yükleme")
        uploaded_file = st.file_uploader(
            "Dosya yükleyin",
            type=[ext[1:] for exts in ALLOWED_EXTENSIONS.values() for ext in exts],
            help="Desteklenen formatlar: Görsel (PNG, JPG, JPEG, GIF, BMP), Döküman (PDF, DOC, DOCX, TXT)"
        )
        
        if uploaded_file:
            with st.spinner("Dosya işleniyor..."):
                extracted_text = process_uploaded_file(uploaded_file)
                if extracted_text:
                    st.success("Dosya başarıyla işlendi!")
                    if "file_content" not in st.session_state:
                        st.session_state.file_content = {}
                    st.session_state.file_content[uploaded_file.name] = extracted_text
                    # Dosya içeriğini veritabanına kaydet
                    save_file_content(uploaded_file.name, extracted_text)
                else:
                    st.error("Dosyadan metin çıkarılamadı.")
        
        # Yüklenen dosyaların listesi
        if "file_content" in st.session_state and st.session_state.file_content:
            st.subheader("📚 Yüklenen Dosyalar")
            for filename in st.session_state.file_content:
                st.text(f"• {filename}")
        
        # Ollama host ayarı
        ollama_host = st.text_input(
            "Ollama Host",
            value="http://localhost:11434",
            help="Ollama API'sinin çalıştığı adres (örn: http://localhost:11434)"
        )
        
        try:
            # Mevcut modelleri al
            response = requests.get(f"{ollama_host}/api/tags")
            if response.status_code == 200:
                models = response.json()
                available_models = [model["name"] for model in models["models"]]
            else:
                available_models = ["llama2", "mistral", "codellama", "neural-chat"]
                st.warning("Model listesi alınamadı. Varsayılan liste kullanılıyor.")
        except Exception as e:
            available_models = ["llama2", "mistral", "codellama", "neural-chat"]
            st.warning("Ollama servisine bağlanılamadı. Varsayılan liste kullanılıyor.")
        
        # Model seçimi
        selected_model = st.selectbox(
            "Model seçin",
            available_models,
            index=0 if available_models else 0
        )
        
        # Model parametreleri
        temperature = st.slider("Yaratıcılık (Temperature)", 0.0, 1.0, 0.7, 0.1)
        
        # Bağlantı durumu
        with st.expander("Bağlantı Durumu"):
            try:
                response = requests.get(f"{ollama_host}/api/version")
                if response.status_code == 200:
                    version_info = response.json()
                    st.success(f"✅ Bağlantı başarılı\nSürüm: {version_info.get('version', 'Bilinmiyor')}")
                else:
                    st.error("❌ Bağlantı başarısız")
            except Exception as e:
                st.error(f"❌ Bağlantı hatası: {str(e)}")
        
        # Sohbeti temizleme butonu
        if st.button("🗑️ Sohbeti Temizle"):
            st.session_state.messages = []
            st.session_state.conversation = None
    
    # Session state başlatma
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Yeni konuşma başlat
        st.session_state.conversation_id = save_conversation(
            st.session_state.username,
            selected_model
        )
    
    # Her host değişikliğinde veya model değişikliğinde conversation'ı yenile
    conversation_key = f"{ollama_host}_{selected_model}"
    if "current_conversation" not in st.session_state or st.session_state.get("current_conversation") != conversation_key:
        # Ollama modeli başlatma
        llm = Ollama(
            model=selected_model,
            temperature=temperature,
            base_url=ollama_host
        )
        
        # Konuşma zinciri oluşturma
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationBufferMemory()
        )
        st.session_state.current_conversation = conversation_key
        # Yeni konuşma başlat
        st.session_state.conversation_id = save_conversation(
            st.session_state.username,
            selected_model
        )
    
    # Mesajları görüntüleme
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Kullanıcı girişi
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Kullanıcı mesajını gösterme
        st.chat_message("user").markdown(prompt)
        
        # Mesajı kaydetme
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.conversation_id, "user", prompt)
        
        try:
            # Dosya içeriğini prompt'a ekle
            if "file_content" in st.session_state and st.session_state.file_content:
                context = "Yüklenen dosyaların içeriği:\n\n"
                for filename, content in st.session_state.file_content.items():
                    context += f"[{filename}]:\n{content}\n\n"
                prompt = context + "\n\nKullanıcı sorusu: " + prompt
            
            # Model yanıtı için placeholder oluştur
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                stream_handler = StreamHandler(message_placeholder)
                
                # Stream yanıtı al
                response = st.session_state.conversation.predict(
                    input=prompt,
                    callbacks=[stream_handler]
                )
                
                # Son yanıtı göster
                message_placeholder.markdown(response)
            
            # Yanıtı kaydetme
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message(st.session_state.conversation_id, "assistant", response)
            
        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")
            if "connection refused" in str(e).lower():
                st.warning(f"Ollama servisine bağlanılamadı. Lütfen Ollama'nın {ollama_host} adresinde çalıştığından emin olun.") 