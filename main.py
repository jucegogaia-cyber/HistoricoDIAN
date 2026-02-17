import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

# Configuración del Sheet (LEXIUS_2026)
SHEET_ID = "1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1985570044"

async def automatizar_dian():
    # 1. Leer los CUFE/CUDE desde el Sheet
    df = pd.read_csv(SHEET_URL)
    codigos_cufe = df['CUFE/CUDE'].dropna().tolist()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        for cufe in codigos_cufe:
            print(f"Buscando documento: {cufe}")
            try:
                # 2. Ir al Buscador de la DIAN
                await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument")
                
                # 3. Pegar el código y buscar
                await page.fill('input[name="DocumentKey"]', cufe) # ID del campo de búsqueda
                await page.click('button[type="submit"]') # Botón Buscar
                
                # 4. Esperar a que cargue la página del documento
                await page.wait_for_url("**/Document/ShowDocumentToPublic**")
                
                # 5. Lógica de descarga del PDF
                async with page.expect_download() as download_info:
                    # Buscamos el botón de descarga (normalmente un icono de PDF)
                    await page.click('a:has-text("Descargar PDF")') 
                
                download = await download_info.value
                await download.save_as(f"./facturas/{cufe}.pdf")
                print(f"✓ Guardado: {cufe}.pdf")
                
            except Exception as e:
                print(f"× Error con {cufe}: {e}")

        await browser.close()

if __name__ == "__main__":
    os.makedirs("./facturas", exist_ok=True)
    asyncio.run(automatizar_dian())
