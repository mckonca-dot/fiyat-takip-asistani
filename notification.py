import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- SENİN BİLGİLERİN (GÖNDERİCİ) ---
SENDER_EMAIL = "mckonca@gmail.com"  
APP_PASSWORD = "xlsk xzne qwme igex" 
# ------------------------------------

# ARTIK 'KIME' PARAMETRESİ ALIYOR
def mail_gonder(urun_adi, eski_fiyat, yeni_fiyat, link, kime_gidecek):
    try:
        subject = f"🔥 İNDİRİM ALARMI: {urun_adi}"
        body = f"Merhaba! Takip ettiğin ürün düştü.\n\nÜrün: {urun_adi}\nFiyat: {yeni_fiyat} TL\nLink: {link}"

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = kime_gidecek # Dinamik alıcı
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, kime_gidecek, msg.as_string())
        server.quit()
        print(f"📧 Mail gönderildi -> {kime_gidecek}")
        return True
    except Exception as e:
        print(f"Mail hatası: {e}")
        return False