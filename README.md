# Ollama Chat

Yerel Ollama modelleriyle sohbet edebileceğiniz bir web uygulaması. Streamlit ve LangChain kullanılarak geliştirilmiştir.

## Özellikler

- 💬 Yerel Ollama modelleriyle sohbet
- 📁 Dosya yükleme ve işleme desteği (PDF, Word, Görsel, Metin)
- 🔍 OCR ile görsel ve PDF'lerden metin çıkarma
- 📊 Vector veritabanı ile benzerlik araması
- 🔐 Kullanıcı girişi ve yetkilendirme
- 💾 Konuşma geçmişi kaydetme
- 🔄 Stream çıktısı desteği

## Gereksinimler

- Python 3.12+
- Ollama (yerel olarak çalışan)
- PostgreSQL (pgvector uzantısı ile)
- Tesseract OCR
- Poppler

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/yourusername/ollama-chat.git
cd ollama-chat
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
.\venv\Scripts\activate  # Windows
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Sistem bağımlılıklarını yükleyin:

macOS:
```bash
brew install tesseract tesseract-lang poppler libmagic
```

Linux:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-tur poppler-utils libmagic1
```

Windows:
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) indirin ve yükleyin
- [Poppler](http://blog.alivate.com.au/poppler-windows/) indirin ve yükleyin

5. `.env` dosyası oluşturun:
```bash
cp .env.example .env
```
Ve gerekli değişkenleri düzenleyin.

6. Uygulamayı başlatın:
```bash
streamlit run app.py
```

## Kullanım

1. Tarayıcınızda `http://localhost:8501` adresine gidin
2. Varsayılan giriş bilgileri:
   - Kullanıcı adı: `admin`
   - Şifre: `admin123`
3. Ollama modelinizi seçin ve sohbete başlayın
4. İsterseniz dosya yükleyerek içeriği hakkında sorular sorabilirsiniz

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Murat - [@yourusername](https://twitter.com/yourusername)

Proje Linki: [https://github.com/yourusername/ollama-chat](https://github.com/yourusername/ollama-chat) 