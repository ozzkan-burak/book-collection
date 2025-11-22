# 📚 Kitap Koleksiyonu Yönetim Uygulaması

Kamera ile kitap kapağını okutarak OCR teknolojisi ile kitaplarınızı koleksiyonunuza ekleyebileceğiniz bir masaüstü uygulaması.

## 🎯 Özellikler

- 📷 **Kamera ile OCR**: Kitap kapağını kameraya göstererek otomatik ekleme
- 📖 **Okunma Durumu**: Okuduğunuz/okumadığınız kitapları takip edin
- 🔍 **Arama ve Filtreleme**: Kitap veya yazar adına göre arama yapın
- ✏️ **Manuel Ekleme**: İsterseniz manuel olarak da kitap ekleyebilirsiniz
- 🗑️ **Silme**: İstenmeyen kitapları silin
- 📚 **Google Books API**: Kitap bilgilerini otomatik olarak zenginleştirin

## 🛠️ Teknoloji Stack

- **Frontend**: Electron (HTML, CSS, JavaScript)
- **Backend**: Python Flask
- **OCR**: Pytesseract
- **Veritabanı**: PostgreSQL
- **API**: Google Books API

## 📋 Gereksinimler

### Sistem Gereksinimleri

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Tesseract OCR

### Tesseract OCR Kurulumu

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-tur tesseract-ocr-eng
```

**macOS:**

```bash
brew install tesseract tesseract-lang
```

**Windows:**

1. [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki) indirin
2. Kurulum sırasında Türkçe dil paketini seçin
3. PATH'e tesseract.exe'nin konumunu ekleyin

## 🚀 Kurulum

### 1. PostgreSQL Veritabanı Kurulumu

```bash
cd database

# .env dosyasını oluşturun (init_db.py içinde DB bilgilerini güncelleyin)
python3 init_db.py
```

### 2. Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyası oluştur
cp .env.example .env
# .env dosyasını düzenleyerek PostgreSQL bilgilerinizi girin

# Flask sunucusunu başlat
python app.py
```

Backend http://127.0.0.1:5000 adresinde çalışacak.

### 3. Electron Uygulaması Kurulumu

```bash
cd electron-app

# Bağımlılıkları yükle
npm install

# Uygulamayı başlat
npm start
```

## 📖 Kullanım

### Kamera ile Kitap Ekleme

1. "📷 Kamerayı Başlat" butonuna tıklayın
2. Kitap kapağını kameraya net bir şekilde gösterin
3. "📸 Fotoğraf Çek" butonuna tıklayın
4. OCR işlemi otomatik olarak çalışacak ve kitap koleksiyonunuza eklenecek

### Manuel Kitap Ekleme

1. "Manuel Kitap Ekle" bölümünden kitap adı ve yazar adını girin
2. İsterseniz "Okudum" kutucuğunu işaretleyin
3. "➕ Kitap Ekle" butonuna tıklayın

### Kitapları Yönetme

- **Filtreleme**: "Tümü", "Okuduklarım", "Okumadıklarım" butonlarını kullanın
- **Arama**: Arama kutusundan kitap veya yazar adına göre arayın
- **Okundu İşaretleme**: Her kitap kartında "📖 Okunmadı" / "✓ Okundu" butonunu kullanın
- **Silme**: "🗑️ Sil" butonu ile kitabı koleksiyondan çıkarın

## 🔧 API Endpoints

### Kitap İşlemleri

- `GET /api/books` - Tüm kitapları getir
- `POST /api/books` - Manuel kitap ekle
- `DELETE /api/books/:id` - Kitap sil
- `PUT /api/books/:id/read-status` - Okundu durumunu güncelle

### OCR İşlemleri

- `POST /api/ocr/scan` - Görüntüden kitap bilgisi çıkar (sadece test için)
- `POST /api/ocr/scan-and-add` - Görüntüyü işle ve veritabanına ekle

### Arama ve Filtreleme

- `GET /api/books/search?q=query` - Kitap ara
- `GET /api/books/filter?isRead=true` - Okunma durumuna göre filtrele

## 📁 Proje Yapısı

```
book-collection/
├── backend/
│   ├── app.py              # Flask uygulaması
│   ├── database.py         # Veritabanı işlemleri
│   ├── ocr_service.py      # OCR ve Google Books API
│   ├── requirements.txt    # Python bağımlılıkları
│   └── .env.example        # Environment değişkenleri
├── database/
│   ├── schema.sql          # PostgreSQL şeması
│   └── init_db.py          # Veritabanı başlatma scripti
└── electron-app/
    ├── main.js             # Electron ana süreç
    ├── package.json        # Node.js bağımlılıkları
    └── renderer/
        ├── index.html      # Arayüz HTML
        ├── styles.css      # CSS stilleri
        └── app.js          # Frontend JavaScript

```

## 🔑 Google Books API (Opsiyonel)

Google Books API kullanmak için:

1. [Google Cloud Console](https://console.cloud.google.com/) üzerinden API Key alın
2. `backend/.env` dosyasına ekleyin:
   ```
   GOOGLE_BOOKS_API_KEY=your_api_key_here
   ```

Not: API key olmadan da kullanabilirsiniz, ancak rate limit daha düşük olacaktır.

## 🐛 Sorun Giderme

### Kamera açılmıyor

- Tarayıcı/Electron'un kamera iznini kontrol edin
- Başka bir uygulama kamerayı kullanıyor olabilir

### OCR çalışmıyor

- Tesseract'ın doğru kurulduğundan emin olun: `tesseract --version`
- Türkçe dil paketinin yüklü olduğunu kontrol edin: `tesseract --list-langs`

### Backend bağlantı hatası

- Flask sunucusunun çalıştığından emin olun (http://127.0.0.1:5000/api/health)
- PostgreSQL veritabanının çalıştığını kontrol edin
- `.env` dosyasındaki veritabanı bilgilerini kontrol edin

### Veritabanı hatası

- PostgreSQL servisinin çalıştığından emin olun: `sudo systemctl status postgresql`
- Veritabanı şemasının oluşturulduğunu kontrol edin

## 📝 Notlar

- OCR başarı oranı kitap kapağının kalitesine bağlıdır
- İyi aydınlatma ve net görüntü daha iyi sonuç verir
- Bazı kitap kapakları OCR için uygun olmayabilir, bu durumda manuel ekleme kullanın

## 📄 Lisans

MIT License

## backend başlatmak için

cd /home/burak/Masaüstü/book-collection/backend && source venv/bin/activate && python app.py

## 👨‍💻 Geliştirici

Burak Özkan
