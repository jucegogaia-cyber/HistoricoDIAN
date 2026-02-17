import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

SHEET_ID = "1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1985570044"

async def automatizar_dian():
    print("🚀 Iniciando Motor Ultra-Resistente...")
    os.makedirs("./facturas", exist_ok=True)
    
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        codigos_cufe = df['CUFE/CUDE'].dropna().tolist()
        print(f"✓ {len(codigos_cufe)} facturas cargadas.")
    except Exception as e:
        print(f"❌ Error en Sheet: {e}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
        page = await context.new_page()

        for cufe in codigos_cufe:
            cufe_limpio = str(cufe).strip()
            print(f"🔍 Intentando con CUFE: {cufe_limpio[:15]}...")
            
            for intento in range(2): # Lo intenta 2 veces por factura
                try:
                    await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", wait_until="networkidle", timeout=90000)
                    await page.wait_for_selector("#DocumentKey", timeout=30000)
                    await page.fill("#DocumentKey", cufe_limpio)
                    
                    # Presionamos Enter y esperamos la carga
                    await page.keyboard.press("Enter")
                    
                    # Esperamos específicamente el visor de documentos (ShowDocumentToPublic)
                    print("⏳ Esperando respuesta de la DIAN (esto puede tardar)...")
                    await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=90000)
                    
                    # Si llegamos aquí, ¡éxito! Buscamos el PDF
                    async with page.expect_download(timeout=60000) as download_info:
                        await page.locator("a:has-text('PDF'), a[title*='PDF']").first.click()
                    
                    download = await download_info.value
                    await download.save_as(f"./facturas/Factura_{cufe_limpio[:10]}.pdf")
                    print(f"✅ ¡LOGRADO! Factura guardada.")
                    break # Sale del bucle de reintentos si tiene éxito

                except Exception as e:
                    print(f"⚠️ Reintento {intento + 1} fallido...")
                    await asyncio.sleep(5) # Pausa antes de reintentar

        await browser.close()

if __name__ == "__main__":
    asyncio.run(automatizar_dian())
