-- Kitap Koleksiyonu Veritabanı Şeması

-- Books tablosu
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    book_title VARCHAR(500) NOT NULL,
    author VARCHAR(255) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index oluştur (arama performansı için)
CREATE INDEX IF NOT EXISTS idx_book_title ON books(book_title);
CREATE INDEX IF NOT EXISTS idx_author ON books(author);

-- Örnek veri (test için)
-- INSERT INTO books (book_title, author, is_read) VALUES ('Suç ve Ceza', 'Fyodor Dostoyevski', TRUE);
-- INSERT INTO books (book_title, author, is_read) VALUES ('1984', 'George Orwell', FALSE);
