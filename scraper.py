from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

def get_product_data(url):
    chrome_options = Options()
    
    # --- 🚀 HIZ VE GİZLİLİK AYARLARI ---
    
    # 1. HAYALET MODU (Pencere Açılmaz)
    chrome_options.add_argument("--headless=new") 
    
    # 2. SANAL EKRAN (Görsel Zeka için ŞART)
    # Pencere açılmasa bile arka planda bu çözünürlükteymiş gibi davranır.
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 3. RESİMLERİ ENGELLE (Büyük Hız Kazandırır)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # 4. SAYFA YÜKLEME STRATEJİSİ (Eager)
    # Sayfanın %100 yüklenmesini (reklamlar, analizler) beklemez. HTML gelince başlar.
    chrome_options.page_load_strategy = 'eager'

    # 5. DİĞER PERFORMANS AYARLARI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage") # Hafıza kullanımını optimize eder
    
    # Bot gizleme (Amazon vs. engellemesin diye)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    
    name = "İsim Bulunamadı"
    price = 0.0

    try:
        # print(f"\n🔎 Analiz ediliyor: {url}") # Konsolu kirletmemek için kapattım
        driver.get(url)
        
        # Bekleme süresini düşürdük çünkü resimler yüklenmiyor
        time.sleep(2) 

        # 1. İSİM BULMA
        try:
            if len(driver.find_elements(By.TAG_NAME, "h1")) > 0:
                name = driver.find_element(By.TAG_NAME, "h1").text
            else:
                name = driver.find_element(By.CLASS_NAME, "product-name").text
        except:
            name = driver.title

        # -----------------------------------------------------------
        # ADIM 2: VIP SINIF KONTROLÜ (Hızlı Sonuç)
        # -----------------------------------------------------------
        found_vip = False
        
        if "trendyol.com" in url:
            try:
                vip_element = driver.find_element(By.CLASS_NAME, "prc-dsc")
                raw_text = vip_element.text
                if raw_text.lower().count("tl") < 2:
                    price = temizle_fiyat(raw_text)
                    if price > 0: found_vip = True
            except: pass

        elif "n11.com" in url:
            try:
                vip_element = driver.find_element(By.CLASS_NAME, "newPrice") 
                if not vip_element: vip_element = driver.find_element(By.TAG_NAME, "ins")
                price = temizle_fiyat(vip_element.text)
                found_vip = True
            except: pass
            
        elif "hepsiburada.com" in url:
             # Hepsiburada için görsel tarama daha sağlıklıdır ama 
             # markup değişmediyse buraya özel id eklenebilir.
             pass

        # -----------------------------------------------------------
        # ADIM 3: GÖRSEL ZEKA & ANTI-MERGE (Eğer VIP bulunamazsa)
        # -----------------------------------------------------------
        if not found_vip:
            potential_elements = driver.find_elements(By.CSS_SELECTOR, "span, div, b, strong, ins")
            candidates = []

            for elem in potential_elements:
                try:
                    text = elem.text.strip()
                    if not text or not any(char.isdigit() for char in text): continue
                    
                    # Anti-Merge: Birden fazla fiyat varsa at
                    if text.lower().count("tl") > 1 or text.lower().count("try") > 1: continue
                    
                    # Üstü çizili fiyatları at (Eski fiyat)
                    if "line-through" in elem.value_of_css_property("text-decoration"): continue
                    
                    val = temizle_fiyat(text)
                    if val <= 10: continue

                    # Font Büyüklüğü (Headless modda window-size sayesinde çalışır)
                    font_size_str = elem.value_of_css_property("font-size") 
                    font_size = float(font_size_str.replace("px", "")) if font_size_str else 0
                    
                    candidates.append((font_size, val, text))
                except: continue

            # En büyük fontlu olanı seç
            candidates.sort(key=lambda x: x[0], reverse=True)

            if candidates:
                price = candidates[0][1]

        # print(f"✅ {price} TL - {name[:20]}...") 
        return {
            "name": name,
            "price": price,
            "url": url
        }

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None
    finally:
        driver.quit()

def temizle_fiyat(text):
    if not text: return 0.0
    text = str(text)
    if "/" in text: text = text.split("/")[0]
    text = text.lower().replace("tl", "").replace("try", "").replace("sepette", "").strip()
    text = re.sub(r'[^\d.,]', '', text)
    if not text: return 0.0

    if "," in text:
        if "." in text: text = text.replace(".", "").replace(",", ".")
        else:
            parts = text.split(",")
            if len(parts[-1]) == 2: text = text.replace(",", ".")
            else: text = text.replace(",", "")
    else:
        parts = text.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3: text = text.replace(".", "")

    try: return float(text)
    except: return 0.0

if __name__ == "__main__":
    print("Modül çalışıyor...")