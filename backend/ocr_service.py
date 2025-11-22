"""
OCR ve Google Books API modülü
"""
import pytesseract
from PIL import Image
import requests
import io
import base64
import re
import os

def process_image_ocr(image_data):
    """
    Base64 kodlu görüntüden OCR ile metin çıkar
    
    Args:
        image_data: Base64 kodlu görüntü string'i (data:image/png;base64,...)
    
    Returns:
        Çıkarılan metin
    """
    try:
        # Base64 header'ını temizle
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Base64'ü decode et
        image_bytes = base64.b64decode(image_data)
        
        # PIL Image'a çevir
        image = Image.open(io.BytesIO(image_bytes))
        
        # OCR ile metin çıkar (Türkçe + İngilizce)
        text = pytesseract.image_to_string(image, lang='tur+eng')
        
        # Metni temizle
        text = text.strip()
        
        return text
    except Exception as e:
        raise Exception(f"OCR işlemi başarısız: {str(e)}")

def clean_book_title(text):
    """
    OCR'dan gelen metni temizle ve muhtemel kitap başlığını çıkar
    """
    # Satır satır ayır
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return None
    
    # En uzun satırı kitap başlığı olarak kabul et (genellikle en büyük font)
    # veya ilk birkaç anlamlı satırı birleştir
    title_candidates = []
    for line in lines[:5]:  # İlk 5 satıra bak
        # Çok kısa satırları atla
        if len(line) > 3:
            title_candidates.append(line)
    
    if title_candidates:
        # En uzun olanı seç
        title = max(title_candidates, key=len)
        # Gereksiz karakterleri temizle
        title = re.sub(r'[^\w\s\-:\'ğüşıöçĞÜŞİÖÇ]', '', title)
        return title.strip()
    
    return None

def search_google_books(query):
    """
    Google Books API'den kitap ara
    
    Args:
        query: Arama sorgusu (kitap başlığı)
    
    Returns:
        dict: {'title': '...', 'author': '...', 'found': True/False}
    """
    try:
        api_key = os.getenv('GOOGLE_BOOKS_API_KEY', '')
        base_url = 'https://www.googleapis.com/books/v1/volumes'
        
        params = {
            'q': query,
            'maxResults': 1,
            'printType': 'books',
            'langRestrict': 'tr|en'
        }
        
        if api_key:
            params['key'] = api_key
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('totalItems', 0) > 0:
            book = data['items'][0]['volumeInfo']
            title = book.get('title', '')
            authors = book.get('authors', [])
            author = ', '.join(authors) if authors else 'Bilinmeyen Yazar'
            
            return {
                'title': title,
                'author': author,
                'found': True
            }
        else:
            return {
                'title': query,
                'author': 'Bilinmeyen Yazar',
                'found': False
            }
    
    except Exception as e:
        # API hatası durumunda OCR'dan gelen veriyi kullan
        return {
            'title': query,
            'author': 'Bilinmeyen Yazar',
            'found': False,
            'error': str(e)
        }
