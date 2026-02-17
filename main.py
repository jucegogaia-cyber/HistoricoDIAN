import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

async def automatizar():
    print(">>> 🚀 ESTRATEGIA DE EMERGENCIA: ACCESO DIRECTO")
    os.makedirs("facturas", exist_ok=True)
    url = "https://docs.google.com/spreadsheets/d/1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc/export?format=csv&gid=1985570044"
    
    try:
        df = pd.read_csv(url)
        codigos = df.iloc[:, 1].dropna().head(5).tolist() 
        
        async with async_playwright() as p:
            # Usamos un navegador con configuración de "evasión" total
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
                locale="es-CO" # Le decimos que estamos en Colombia
            )
            page = await context.new_page()
            
            for cufe in codigos:
                print(f"🔍 Intentando CUFE: {cufe[:15]}")
                try:
                    # Vamos directo a la búsqueda
                    await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", timeout=60000)
                    await page.fill("#DocumentKey", str(cufe).strip())
                    
                    # En lugar de solo click, presionamos Enter y esperamos CUALQUIER cambio
                    await page.keyboard.press("Enter")
                    
                    # Si en 20 segundos no carga el visor, tomamos evidencia
                    try:
                        await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=20000)
                        async with page.expect_download(timeout=10000) as download_info:
                            await page.click("a:has-text('PDF')")
                        download = await download_info.value
                        await download.save_as(f"facturas/Factura_{cufe[:10]}.pdf")
                        print("✅ PDF Guardado.")
                    except:
                        # Si falla el visor, tomamos una FOTO para ver el error de la DIAN
                        await page.screenshot(path=f"facturas/CAPTURA_{cufe[:10]}.png")
                        print("⚠️ No abrió visor, captura guardada.")
                        
                except Exception as e:
                    print(f"❌ Error en este código: {e}")
            
            await browser.close()
    except Exception as e:
        print(f"❌ Error General: {e}")

if __name__ == "__main__":
    asyncio.run(automatizar())
