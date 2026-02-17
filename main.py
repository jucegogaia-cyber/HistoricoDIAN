import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def automatizar():
    print(">>> 1. INICIANDO SCRIPT...")
    os.makedirs("facturas", exist_ok=True)
    
    # URL de tu Sheet
    url = "https://docs.google.com/spreadsheets/d/1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc/export?format=csv&gid=1985570044"
    
    try:
        print(">>> 2. LEYENDO GOOGLE SHEET...")
        df = pd.read_csv(url)
        codigos = df.iloc[:, 1].dropna().head(5).tolist() # Solo probaremos con las primeras 5
        print(f">>> 3. ENCONTRADOS {len(codigos)} CODIGOS. EMPEZANDO NAVEGACION...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for cufe in codigos:
                print(f"🔍 BUSCANDO: {cufe[:15]}...")
                await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument")
                await page.fill("#DocumentKey", str(cufe).strip())
                await page.keyboard.press("Enter")
                
                # Esperamos un poco a ver si carga
                await asyncio.sleep(5) 
                # Tomamos una foto para saber qué ve el bot (esto ayuda mucho)
                await page.screenshot(path=f"facturas/foto_{cufe[:5]}.png")
                print(f"📸 Foto tomada para el codigo {cufe[:5]}")
                
            await browser.close()
    except Exception as e:
        print(f"❌ ERROR DETECTADO: {e}")

if __name__ == "__main__":
    asyncio.run(automatizar())
