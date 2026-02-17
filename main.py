import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Iniciamos el navegador en modo incógnito/stealth
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Intentando acceder a la página...")
        # Cambia esta URL por la que necesites de la DIAN o Cloudflare
        await page.goto("https://www.cloudflare.com/es-es/", wait_until="networkidle")
        
        titulo = await page.title()
        print(f"Conexión exitosa. Título: {titulo}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
