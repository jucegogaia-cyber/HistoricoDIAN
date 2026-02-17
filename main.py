import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def automatizar():
    print(">>> INICIANDO DESCARGA (TÁCTICA DE CARGA RÁPIDA)...")
    os.makedirs("facturas", exist_ok=True)
    url = "https://docs.google.com/spreadsheets/d/1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc/export?format=csv&gid=1985570044"
    
    try:
        df = pd.read_csv(url)
        codigos = df.iloc[:, 1].dropna().head(10).tolist() 
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Añadimos un tiempo de espera global de 60 segundos
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
            page = await context.new_page()
            page.set_default_timeout(60000) 
            
            for cufe in codigos:
                cufe_str = str(cufe).strip()
                print(f"🚀 Procesando CUFE: {cufe_str[:15]}...")
                try:
                    # CAMBIO CLAVE: "domcontentloaded" en lugar de "networkidle"
                    await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", wait_until="domcontentloaded")
                    
                    await page.wait_for_selector("#DocumentKey", state="visible")
                    await page.fill("#DocumentKey", cufe_str)
                    await page.keyboard.press("Enter")
                    
                    print("⏳ Esperando visor de factura...")
                    # Esperamos que la URL cambie al visor
                    await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=60000)
                    
                    async with page.expect_download() as download_info:
                        # Intentamos hacer clic en el botón de PDF
                        await page.click("a[title='Descargar PDF'], .btn-download-pdf")
                    
                    download = await download_info.value
                    await download.save_as(f"facturas/Factura_{cufe_str[:10]}.pdf")
                    print(f"✅ PDF GUARDADO: {cufe_str[:10]}")
                    
                except Exception as inner_e:
                    print(f"⚠️ Error individual en {cufe_str[:10]}: {inner_e}")
                    # Si falla una, seguimos con la siguiente
                    continue
                
            await browser.close()
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")

if __name__ == "__main__":
    asyncio.run(automatizar())
