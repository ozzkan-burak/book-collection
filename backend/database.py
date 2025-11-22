"""
Veritabanı bağlantı modülü
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """PostgreSQL veritabanına bağlantı oluştur"""
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'book_collection'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

def add_book(book_title, author, is_read=False):
    """Yeni kitap ekle"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO books (book_title, author, is_read) VALUES (%s, %s, %s) RETURNING id",
            (book_title, author, is_read)
        )
        book_id = cursor.fetchone()['id']
        conn.commit()
        return book_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_all_books():
    """Tüm kitapları getir"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, book_title, author, is_read, created_at FROM books ORDER BY created_at DESC"
        )
        books = cursor.fetchall()
        return books
    finally:
        cursor.close()
        conn.close()

def search_books(query):
    """Kitap ara (başlık veya yazara göre)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT id, book_title, author, is_read, created_at 
            FROM books 
            WHERE book_title ILIKE %s OR author ILIKE %s
            ORDER BY created_at DESC
            """,
            (f'%{query}%', f'%{query}%')
        )
        books = cursor.fetchall()
        return books
    finally:
        cursor.close()
        conn.close()

def book_exists(book_title):
    """Kitap zaten veritabanında var mı kontrol et"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id FROM books WHERE book_title ILIKE %s LIMIT 1",
            (book_title,)
        )
        book = cursor.fetchone()
        return book is not None
    finally:
        cursor.close()
        conn.close()

def delete_book(book_id):
    """Kitap sil"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def update_book_read_status(book_id, is_read):
    """Kitabın okundu durumunu güncelle"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE books SET is_read = %s WHERE id = %s",
            (is_read, book_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_books_by_read_status(is_read):
    """Okunma durumuna göre kitapları getir"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, book_title, author, is_read, created_at FROM books WHERE is_read = %s ORDER BY created_at DESC",
            (is_read,)
        )
        books = cursor.fetchall()
        return books
    finally:
        cursor.close()
        conn.close()
