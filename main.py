from scraper import get_product_data
from database import init_db, add_product
import sqlite3

# 1. Veritabanını hazırla (Eğer yoksa oluşturur)
init_db()

# 2. Takip edilecek ürün linki (Senin az önceki linkin)
url = "https://www.trendyol.com/pleksan/geri-vites-plaka-cami-renault-r12-tsw-sw-p2514-nur-p-42358564"

print("Bot çalışıyor, ürün bilgileri çekiliyor...")

# 3. Scraper'ı çalıştır
urun_bilgisi = get_product_data(url)

if urun_bilgisi:
    print(f"\nSiteden Gelen Veri: {urun_bilgisi['name']} - {urun_bilgisi['price']} TL")
    
    # 4. Veritabanına Kaydet
    add_product(urun_bilgisi['name'], urun_bilgisi['url'], urun_bilgisi['price'])
    print("✅ Başarıyla veritabanına kaydedildi!")
    
    # 5. KONTROL: Veritabanını okuyup ekrana basalım (Dosyayı açamıyordun ya, işte böyle göreceğiz)
    print("\n--- VERİTABANI İÇERİĞİ ---")
    conn = sqlite3.connect("fiyat_takip.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    urunler = cursor.fetchall()
    
    for urun in urunler:
        print(f"ID: {urun[0]} | İsim: {urun[1]} | Fiyat: {urun[3]} TL | Tarih: {urun[4]}")
        
    conn.close()
    
else:
    print("❌ Veri çekilemedi.")