import asyncio
import pandas as pd
import os
import random
from playwright.async_api import async_playwright

async def automatizar():
    print(">>> 🚨 INICIANDO ÚLTIMO INTENTO EN GITHUB (MODO SIGILO)...")
    os.makedirs("facturas", exist_ok=True)
    url = "https://docs.google.com/spreadsheets/d/1BndW6FjIHhIWeF7ik1WdxFKdScBX_ZwpDZhLCJ6upGc/export?format=csv&gid=1985570044"
    
    try:
        df = pd.read_csv(url)
        # Probaremos solo con los primeros 5 códigos para ser rápidos
        codigos = df.iloc[:, 1].dropna().head(5).tolist() 
        
        async with async_playwright() as p:
            # Simulamos un navegador totalmente común
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            for cufe in codigos:
                cufe_str = str(cufe).strip()
                print(f"🔍 Probando CUFE: {cufe_str[:15]}...")
                
                try:
                    # Entramos a la página con tiempo de espera largo
                    await page.goto("https://catalogo-vpfe.dian.gov.co/User/SearchDocument", wait_until="load", timeout=90000)
                    
                    # Esperamos un momento aleatorio para parecer humanos
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Escribimos el CUFE simulando pulsaciones de teclas
                    await page.click("#DocumentKey")
                    await page.type("#DocumentKey", cufe_str, delay=random.randint(50, 150))
                    
                    # Clic en buscar y esperamos
                    await page.click("#btnSearchDocument")
                    print("⏳ Procesando búsqueda...")
                    
                    # Damos 30 segundos para ver si carga el visor
                    try:
                        await page.wait_for_url("**/Document/ShowDocumentToPublic**", timeout=30000)
                        
                        # Si entra, descargamos el PDF
                        async with page.expect_download(timeout=15000) as download_info:
                            await page.locator("a:has-text('PDF')").first.click()
                        
                        download = await download_info.value
                        await download.save_as(f"facturas/Factura_{cufe_str[:10]}.pdf")
                        print(f"✅ ¡PDF DESCARGADO!")
                    
                    except:
                        # Si no entra al visor, tomamos una prueba de qué está viendo el bot
                        nombre_foto = f"facturas/PRUEBA_{cufe_str[:10]}.png"
                        await page.screenshot(path=nombre_foto, full_page=True)
                        print(f"⚠️ No abrió visor. Evidencia guardada en {nombre_foto}")
                        
                except Exception as e:
                    print(f"❌ Error en este CUFE: {e}")
                
                # Pausa entre una factura y otra
                await asyncio.sleep(5)
                
            await browser.close()
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    asyncio.run(automatizar())
