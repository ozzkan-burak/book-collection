"""
PostgreSQL veritabanını başlatma scripti
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Veritabanı bağlantı bilgileri
DB_NAME = "book_collection"
DB_USER = "postgres"  # Kendi PostgreSQL kullanıcı adınızı kullanın
DB_PASSWORD = "postgres"  # Kendi şifrenizi kullanın
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Veritabanını oluştur"""
    try:
        # postgres veritabanına bağlan
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Veritabanı var mı kontrol et
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✓ '{DB_NAME}' veritabanı oluşturuldu")
        else:
            print(f"✓ '{DB_NAME}' veritabanı zaten mevcut")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Veritabanı oluşturulurken hata: {e}")
        return False
    
    return True

def create_tables():
    """Tabloları oluştur"""
    try:
        # book_collection veritabanına bağlan
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Schema dosyasını oku ve çalıştır
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        print("✓ Tablolar başarıyla oluşturuldu")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Tablolar oluşturulurken hata: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("PostgreSQL veritabanı başlatılıyor...\n")
    
    if create_database():
        if create_tables():
            print("\n✓ Veritabanı başlatma tamamlandı!")
        else:
            print("\n✗ Tablo oluşturma başarısız!")
    else:
        print("\n✗ Veritabanı oluşturma başarısız!")
