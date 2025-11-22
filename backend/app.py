"""
Flask Backend API - Kitap Koleksiyonu
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from database import (
    add_book, 
    get_all_books, 
    search_books, 
    book_exists,
    delete_book,
    update_book_read_status,
    get_books_by_read_status
)
from ocr_service import process_image_ocr, extract_book_info

load_dotenv()

app = Flask(__name__)
CORS(app)  # Electron'dan gelen isteklere izin ver

@app.route('/api/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({'status': 'ok', 'message': 'Backend çalışıyor'})

@app.route('/api/books', methods=['GET'])
def get_books():
    """Tüm kitapları getir"""
    try:
        books = get_all_books()
        return jsonify({'success': True, 'books': books})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/books/search', methods=['GET'])
def search():
    """Kitap ara"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'error': 'Arama sorgusu boş olamaz'}), 400
    
    try:
        books = search_books(query)
        return jsonify({'success': True, 'books': books})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book_manual():
    """Manuel kitap ekle"""
    data = request.json
    
    title = data.get('title', '').strip()
    author = data.get('author', '').strip()
    is_read = data.get('isRead', False)  # Frontend'den isRead gelecek
    
    if not title or not author:
        return jsonify({'success': False, 'error': 'Kitap adı ve yazar zorunludur'}), 400
    
    try:
        # Kitap zaten var mı kontrol et
        if book_exists(title):
            return jsonify({
                'success': False, 
                'error': 'Bu kitap zaten koleksiyonunuzda mevcut'
            }), 409
        
        book_id = add_book(title, author, is_read)
        return jsonify({
            'success': True, 
            'message': 'Kitap başarıyla eklendi',
            'book_id': book_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    """Kitap sil"""
    try:
        deleted = delete_book(book_id)
        if deleted:
            return jsonify({'success': True, 'message': 'Kitap silindi'})
        else:
            return jsonify({'success': False, 'error': 'Kitap bulunamadı'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/books/<int:book_id>/read-status', methods=['PUT'])
def update_read_status(book_id):
    """Kitabın okundu durumunu güncelle"""
    data = request.json
    is_read = data.get('isRead', False)
    
    try:
        updated = update_book_read_status(book_id, is_read)
        if updated:
            return jsonify({'success': True, 'message': 'Durum güncellendi'})
        else:
            return jsonify({'success': False, 'error': 'Kitap bulunamadı'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/books/filter', methods=['GET'])
def filter_books():
    """Kitapları okunma durumuna göre filtrele"""
    read_status = request.args.get('isRead', '').lower()
    
    if read_status not in ['true', 'false']:
        return jsonify({'success': False, 'error': 'isRead parametresi true veya false olmalı'}), 400
    
    is_read = read_status == 'true'
    
    try:
        books = get_books_by_read_status(is_read)
        return jsonify({'success': True, 'books': books})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ocr/scan', methods=['POST'])
def scan_book():
    """
    Kameradan gelen görüntüyü OCR ile işle ve kitap bilgilerini döndür
    """
    data = request.json
    image_data = data.get('image', '')
    
    if not image_data:
        return jsonify({'success': False, 'error': 'Görüntü verisi bulunamadı'}), 400
    
    try:
        # OCR ile metni çıkar
        ocr_text = process_image_ocr(image_data)
        
        if not ocr_text:
            return jsonify({
                'success': False, 
                'error': 'Görüntüden metin çıkarılamadı'
            }), 400
        
        # Kitap başlığını ve yazarı çıkar
        book_title, author = extract_book_info(ocr_text)
        
        if not book_title:
            return jsonify({
                'success': False,
                'error': 'Kitap başlığı tespit edilemedi',
                'ocr_text': ocr_text
            }), 400
        
        return jsonify({
            'success': True,
            'title': book_title,
            'author': author or ''
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
