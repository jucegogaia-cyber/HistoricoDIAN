import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def automatizar():
    print(">>> INICIANDO DESCARGA REAL DE PDFS...")
    os.makedirs("facturas", exist_ok=True)
    url = "https://docs.google.com/spreadsheets/d/1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc/export?format=csv&gid=1985570044"
    
    try:
        df = pd.read_csv(url)
        # Probemos con 10 para no saturar
        codigos = df.iloc[:, 1].dropna().head(10).tolist() 
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for cufe in codigos:
                cufe_str = str(cufe).strip()
                print(f"🚀 Procesando CUFE: {cufe_str[:15]}...")
                await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", wait_until="networkidle")
                await page.fill("#DocumentKey", cufe_str)
                await page.keyboard.press("Enter")
                
                # Esperamos a que cargue el visor (esto es clave)
                await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=60000)
                
                # Intentamos descargar el PDF
                async with page.expect_download() as download_info:
                    # Buscamos el botón de descarga por su icono o texto
                    await page.click("a[title='Descargar PDF'], .btn-download-pdf")
                
                download = await download_info.value
                await download.save_as(f"facturas/Factura_{cufe_str[:10]}.pdf")
                print(f"✅ PDF GUARDADO: {cufe_str[:10]}")
                
            await browser.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(automatizar())
