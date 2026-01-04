import sqlite3

def fiyati_yukselt():
    # Veritabanına bağlan
    conn = sqlite3.connect("fiyat_takip.db")
    cursor = conn.cursor()

    # Sistemdeki ürünleri listele
    cursor.execute("SELECT id, isim, fiyat FROM urunler")
    urunler = cursor.fetchall()

    if not urunler:
        print("❌ Veritabanında hiç ürün yok! Önce siteye girip bir link ekle.")
        return

    print("\n--- MEVCUT ÜRÜNLER ---")
    for u in urunler:
        print(f"ID: {u[0]} | Fiyat: {u[2]} TL | İsim: {u[1]}")

    # Kullanıcıdan hangi ürünü değiştireceğini iste
    hedef_id = input("\nFiyatını yükseltmek istediğin ürünün ID'sini yaz: ")
    
    # O ürünü bul
    cursor.execute("SELECT fiyat FROM urunler WHERE id = ?", (hedef_id,))
    veri = cursor.fetchone()

    if veri:
        eski_fiyat = veri[0]
        # Fiyatı %50 artır (Yapay zam)
        yeni_sahte_fiyat = float(eski_fiyat) * 1.5 
        
        # Veritabanını güncelle
        cursor.execute("UPDATE urunler SET fiyat = ? WHERE id = ?", (yeni_sahte_fiyat, hedef_id))
        conn.commit()
        
        print(f"\n✅ HİLE YAPILDI! Ürünün fiyatı {eski_fiyat} TL'den {yeni_sahte_fiyat} TL'ye çıkarıldı.")
        print("Şimdi 'api.py' çalıştığında fiyatı tekrar eski haline (gerçek fiyata) düşmüş görecek ve MAİL ATACAK! 📉📧")
    else:
        print("❌ Geçersiz ID girdin.")

    conn.close()

if __name__ == "__main__":
    fiyati_yukselt()