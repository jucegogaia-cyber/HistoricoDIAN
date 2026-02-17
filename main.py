import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

SHEET_ID = "1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1985570044"

async def automatizar_dian():
    print("🚀 Iniciando Motor de Extracción DIAN...")
    os.makedirs("./facturas", exist_ok=True)
    
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        codigos_cufe = df['CUFE/CUDE'].dropna().tolist()
        print(f"✓ {len(codigos_cufe)} facturas detectadas en LEXIUS_2026.")
    except Exception as e:
        print(f"❌ Error leyendo el Sheet: {e}")
        return

    async with async_playwright() as p:
        # Usamos Chromium con configuraciones para evitar bloqueos
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        for cufe in codigos_cufe:
            print(f"🔍 Procesando CUFE: {cufe[:15]}...")
            try:
                # 1. Entrar al buscador
                await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", wait_until="networkidle")
                
                # 2. Escribir el CUFE
                await page.wait_for_selector("#DocumentKey", timeout=15000)
                await page.fill("#DocumentKey", str(cufe).strip())
                
                # 3. Accionar la búsqueda (Presionando Enter + Clic en Buscar)
                await page.keyboard.press("Enter")
                # Intentamos clic por ID que usa la DIAN
                await page.click("#btnSearchDocument")
                
                # 4. ESPERAR EL SEGUNDO LINK (ShowDocumentToPublic)
                # Damos hasta 30 segundos porque la DIAN a veces es lenta
                print("⏳ Esperando que cargue el visor de factura...")
                await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=40000)
                
                # 5. Descargar el PDF
                async with page.expect_download() as download_info:
                    # Buscamos el botón de descarga dentro del nuevo link
                    await page.click("a[title='Descargar PDF'], .btn-download-pdf")
                
                download = await download_info.value
                await download.save_as(f"./facturas/Factura_{cufe[:10]}.pdf")
                print(f"✅ Factura guardada correctamente.")
                
                # Pausa de seguridad
                await asyncio.sleep(3)

            except Exception as e:
                print(f"⚠️ Saltando {cufe[:10]} debido a demora en el portal.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(automatizar_dian())
