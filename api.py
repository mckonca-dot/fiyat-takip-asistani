from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from scraper import get_product_data
from mail import mail_gonder # Postacı modülümüzü çağırdık
from apscheduler.schedulers.asyncio import AsyncIOScheduler # Zamanlayıcı
from contextlib import asynccontextmanager

# --- ZAMANLAYICI AYARI ---
scheduler = AsyncIOScheduler()

# Otomatik kontrol fonksiyonu
async def otomatik_fiyat_kontrolu():
    print("\n⏰ ----------------------------------------")
    print("⏰ Otomatik kontrol taraması başladı...")
    
    try:
        conn = baglanti_olustur()
        cursor = conn.cursor()
        cursor.execute("SELECT id, isim, fiyat, link, email FROM urunler")
        urunler = cursor.fetchall()
        
        print(f"📋 Takip listesinde {len(urunler)} ürün var.")
        
        for urun in urunler:
            uid = urun[0]
            isim = urun[1]
            eski_fiyat = float(urun[2]) # Sayı olduğundan emin olalım
            link = urun[3]
            email = urun[4]
            
            print(f"\n🔎 İNCELENİYOR: {isim[:20]}...")
            print(f"   💾 Veritabanındaki Fiyat: {eski_fiyat} TL")
            
            # Güncel fiyatı çek
            yeni_veri = get_product_data(link)
            
            if yeni_veri:
                yeni_fiyat = float(yeni_veri['price'])
                print(f"   🌍 Siteden Çekilen Fiyat: {yeni_fiyat} TL")
                
                # KARŞILAŞTIRMA ANI
                if yeni_fiyat != eski_fiyat:
                    print(f"   ⚡ FARK TESPİT EDİLDİ! ({eski_fiyat} -> {yeni_fiyat})")
                    
                    # Veritabanını güncelle
                    cursor.execute("UPDATE urunler SET fiyat = ? WHERE id = ?", (yeni_fiyat, uid))
                    cursor.execute("INSERT INTO fiyatlar (urun_id, fiyat) VALUES (?, ?)", (uid, yeni_fiyat))
                    print(f"   💾 Veritabanı güncellendi.")

                    # 🔥 EĞER FİYAT DÜŞMÜŞSE MAIL AT 🔥
                    if yeni_fiyat < eski_fiyat:
                        print("   📉 İNDİRİM VAR! Mail gönderiliyor...")
                        basari = mail_gonder(email, isim, eski_fiyat, yeni_fiyat, link)
                        if basari:
                            print("   ✅ Mail başarıyla gitti.")
                        else:
                            print("   ❌ Mail gönderilemedi (Mail ayarlarını kontrol et).")
                    else:
                        print("   📈 Fiyat artmış, mail atılmıyor.")
                else:
                    print("   😐 Fiyat aynı, değişiklik yok.")
            else:
                print("   ⚠️ Veri çekilemedi (Scraper 0 veya None döndürdü).")
        
        conn.commit()
        conn.close()
        print("\n✅ Tarama tamamlandı.")
        print("⏰ ----------------------------------------\n")

    except Exception as e:
        print(f"❌ KONTROL SIRASINDA HATA: {e}")

# Uygulama başlarken zamanlayıcıyı çalıştır
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Burada süreyi ayarlıyoruz: minutes=60 (Saat başı)
    # Test için minutes=1 yapabilirsin.
    scheduler.add_job(otomatik_fiyat_kontrolu, 'interval', minutes=1)
    scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)

# --- AYARLAR (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def baglanti_olustur():
    conn = sqlite3.connect("fiyat_takip.db")
    return conn

def tablo_olustur():
    conn = baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            fiyat REAL,
            link TEXT,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiyatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_id INTEGER,
            fiyat REAL,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(urun_id) REFERENCES urunler(id)
        )
    """)
    conn.commit()
    conn.close()

tablo_olustur()

class UrunEkle(BaseModel):
    url: str
    email: str

# --- ENDPOINTLER ---

@app.post("/ekle")
def urun_ekle(veri: UrunEkle):
    sonuc = get_product_data(veri.url)
    if not sonuc:
        return {"hata": "Veri çekilemedi"}
    
    conn = baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urunler (isim, fiyat, link, email) VALUES (?, ?, ?, ?)", 
                   (sonuc['name'], sonuc['price'], veri.url, veri.email))
    urun_id = cursor.lastrowid
    cursor.execute("INSERT INTO fiyatlar (urun_id, fiyat) VALUES (?, ?)", (urun_id, sonuc['price']))
    conn.commit()
    conn.close()
    return {"mesaj": "Ürün eklendi", "veri": sonuc}

@app.get("/urunler/{email}")
def urunleri_getir(email: str):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.isim, u.fiyat, u.link, MAX(f.tarih) as son_tarih 
        FROM urunler u 
        LEFT JOIN fiyatlar f ON u.id = f.urun_id 
        WHERE u.email = ? 
        GROUP BY u.id
    """, (email,))
    urunler = cursor.fetchall()
    conn.close()
    liste = []
    for u in urunler:
        liste.append({
            "id": u[0],
            "isim": u[1],
            "fiyat": u[2],
            "link": u[3],
            "tarih": u[4]
        })
    return liste

@app.get("/kontrol-et")
async def fiyatlari_guncelle():
    # Manuel kontrol butonu için bu fonksiyonu kullanıyoruz
    await otomatik_fiyat_kontrolu()
    return {"mesaj": "Kontrol tamamlandı"}

@app.get("/gecmis/{urun_id}")
def gecmis_getir(urun_id: int):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("SELECT tarih, fiyat FROM fiyatlar WHERE urun_id = ? ORDER BY id ASC", (urun_id,))
    veriler = cursor.fetchall()
    conn.close()
    liste = []
    for v in veriler:
        liste.append({"name": v[0], "fiyat": v[1]})
    return liste

@app.delete("/sil/{urun_id}")
def urun_sil(urun_id: int):
    try:
        conn = baglanti_olustur()
        cursor = conn.cursor()
        print(f"🗑️ Silme isteği geldi: ID {urun_id}")
        cursor.execute("DELETE FROM fiyatlar WHERE urun_id = ?", (urun_id,))
        cursor.execute("DELETE FROM urunler WHERE id = ?", (urun_id,))
        conn.commit()
        conn.close()
        return {"mesaj": "Ürün silindi"}
    except Exception as e:
        print(f"❌ SİLME HATASI: {e}")
        raise HTTPException(status_code=500, detail=str(e))