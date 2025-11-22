// Backend API URL
const API_URL = 'http://127.0.0.1:5000/api';

// DOM Elementleri
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const captureBtn = document.getElementById('captureBtn');
const stopCameraBtn = document.getElementById('stopCamera');
const statusDiv = document.getElementById('status');
const booksList = document.getElementById('booksList');
const manualAddForm = document.getElementById('manualAddForm');
const searchInput = document.getElementById('searchInput');
const filterBtns = document.querySelectorAll('.filter-btn');

let stream = null;
let currentFilter = 'all';

// Kamera başlat
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        video.srcObject = stream;
        
        startCameraBtn.style.display = 'none';
        captureBtn.style.display = 'inline-block';
        stopCameraBtn.style.display = 'inline-block';
        
        showStatus('Kamera başlatıldı! Kitap kapağını gösterin.', 'info');
    } catch (error) {
        showStatus('Kamera erişimi reddedildi: ' + error.message, 'error');
    }
});

// Fotoğraf çek ve OCR yap
captureBtn.addEventListener('click', async () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    // Canvas'ı base64'e çevir
    const imageData = canvas.toDataURL('image/png');
    
    showStatus('Kitap kapağı işleniyor... Lütfen bekleyin.', 'info');
    captureBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/ocr/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Input alanlarına doldur
            document.getElementById('bookTitle').value = result.title;
            document.getElementById('bookAuthor').value = result.author;
            
            showStatus('✅ Kitap bilgileri algılandı! Kontrol edip kaydedin.', 'success');
            
            // Manuel ekleme bölümüne scroll yap
            document.querySelector('.manual-add-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            showStatus('❌ ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('❌ Bağlantı hatası: ' + error.message, 'error');
    } finally {
        captureBtn.disabled = false;
    }
});

// Kamerayı durdur
stopCameraBtn.addEventListener('click', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        stream = null;
    }
    
    startCameraBtn.style.display = 'inline-block';
    captureBtn.style.display = 'none';
    stopCameraBtn.style.display = 'none';
    
    showStatus('Kamera durduruldu.', 'info');
});

// Manuel kitap ekle
manualAddForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('bookTitle').value.trim();
    const author = document.getElementById('bookAuthor').value.trim();
    const isRead = document.getElementById('isRead').checked;
    
    if (!title || !author) {
        showStatus('Lütfen kitap adı ve yazar adını girin.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, author, isRead })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showTooltip('✅ Kitap başarıyla kaydedildi!');
            showStatus(`✅ "${title}" kitabı koleksiyonunuza eklendi!`, 'success');
            manualAddForm.reset();
            loadBooks();
        } else {
            showStatus('❌ ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('❌ Bağlantı hatası: ' + error.message, 'error');
    }
});

// Kitapları yükle
async function loadBooks() {
    try {
        let url = `${API_URL}/books`;
        
        if (currentFilter === 'read') {
            url = `${API_URL}/books/filter?isRead=true`;
        } else if (currentFilter === 'unread') {
            url = `${API_URL}/books/filter?isRead=false`;
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            displayBooks(result.books);
        } else {
            booksList.innerHTML = '<p class="error">Kitaplar yüklenemedi.</p>';
        }
    } catch (error) {
        booksList.innerHTML = '<p class="error">Backend bağlantısı kurulamadı. Flask sunucusunun çalıştığından emin olun.</p>';
    }
}

// Kitapları göster
function displayBooks(books) {
    if (books.length === 0) {
        booksList.innerHTML = '<p class="empty-state">Henüz kitap eklenmemiş. Kamera ile kitap kapağını okutarak başlayın!</p>';
        return;
    }
    
    booksList.innerHTML = books.map(book => `
        <div class="book-card ${book.is_read ? 'read' : ''}">
            <div class="book-title">${book.book_title}</div>
            <div class="book-author">✍️ ${book.author}</div>
            <div class="book-actions">
                <button class="btn ${book.is_read ? 'btn-secondary' : 'btn-success'}" 
                        onclick="toggleReadStatus(${book.id}, ${!book.is_read})">
                    ${book.is_read ? '✓ Okundu' : '📖 Okunmadı'}
                </button>
                <button class="btn btn-danger" onclick="deleteBook(${book.id})">
                    🗑️ Sil
                </button>
            </div>
        </div>
    `).join('');
}

// Okundu durumunu değiştir
async function toggleReadStatus(bookId, isRead) {
    try {
        const response = await fetch(`${API_URL}/books/${bookId}/read-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ isRead })
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadBooks();
        } else {
            showStatus('❌ Durum güncellenemedi: ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('❌ Bağlantı hatası: ' + error.message, 'error');
    }
}

// Kitap sil
async function deleteBook(bookId) {
    if (!confirm('Bu kitabı silmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/books/${bookId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('✅ Kitap silindi.', 'success');
            loadBooks();
        } else {
            showStatus('❌ Kitap silinemedi: ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('❌ Bağlantı hatası: ' + error.message, 'error');
    }
}

// Arama
searchInput.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    
    if (query.length < 2) {
        loadBooks();
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/books/search?q=${encodeURIComponent(query)}`);
        const result = await response.json();
        
        if (result.success) {
            displayBooks(result.books);
        }
    } catch (error) {
        console.error('Arama hatası:', error);
    }
});

// Filtreler
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        currentFilter = btn.dataset.filter;
        loadBooks();
    });
});

// Status mesajı göster
function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status-message show ${type}`;
    
    setTimeout(() => {
        statusDiv.classList.remove('show');
    }, 5000);
}

// Tooltip göster
function showTooltip(message) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-notification';
    tooltip.textContent = message;
    document.body.appendChild(tooltip);
    
    setTimeout(() => {
        tooltip.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        tooltip.classList.remove('show');
        setTimeout(() => tooltip.remove(), 300);
    }, 3000);
}

// Sayfa yüklendiğinde kitapları getir
window.addEventListener('DOMContentLoaded', () => {
    loadBooks();
});
