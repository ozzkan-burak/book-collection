"""
OCR ve Google Books API modülü
"""
import pytesseract
from PIL import Image, ImageEnhance
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
        
        # Görüntü ön işleme - kontrastı artır
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Griye çevir
        image = image.convert('L')
        
        # OCR ile metin çıkar (Türkçe + İngilizce)
        # PSM 3: Tam otomatik sayfa segmentasyonu
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(image, lang='tur+eng', config=custom_config)
        
        # Metni temizle
        text = text.strip()
        
        print(f"[DEBUG] OCR çıktısı uzunluğu: {len(text)} karakter")
        
        return text
    except Exception as e:
        raise Exception(f"OCR işlemi başarısız: {str(e)}")

def extract_book_info(text):
    """
    OCR'dan gelen metinden kitap adı ve yazar bilgisini çıkar
    
    Returns:
        tuple: (book_title, author)
    """
    print(f"[DEBUG] OCR Ham Metin:\n{text}\n")
    
    # Satır satır ayır
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        print("[DEBUG] Hiç satır bulunamadı")
        return None, None
    
    print(f"[DEBUG] Bulunan satırlar: {lines}")
    
    # Anlamlı satırları filtrele
    valid_lines = []
    for line in lines[:10]:
        if len(line) > 2:
            # Gereksiz karakterleri temizle
            cleaned = re.sub(r'[^\w\s\-:\'ğüşıöçĞÜŞİÖÇ.,!?]', '', line).strip()
            if len(cleaned) > 2:
                valid_lines.append(cleaned)
    
    if not valid_lines:
        print("[DEBUG] Hiç geçerli satır bulunamadı")
        return None, None
    
    # İlk satır genellikle kitap adı, ikinci satır yazar
    book_title = valid_lines[0]
    author = valid_lines[1] if len(valid_lines) > 1 else None
    
    print(f"[DEBUG] Kitap adı: {book_title}")
    print(f"[DEBUG] Yazar: {author}")
    
    return book_title, author
