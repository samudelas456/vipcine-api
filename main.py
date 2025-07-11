import asyncio
import json
import requests
from playwright.async_api import async_playwright

FIREBASE_URL = "https://smartflix-73adf-default-rtdb.firebaseio.com/canais.json"

async def pegar_canais():
    canais = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        await page.goto("https://redecanaistv.gs/", timeout=60000)
        await page.wait_for_selector("div.canais")

        elementos = await page.query_selector_all("div.canais > div")

        for el in elementos[:10]:
            try:
                nome = await el.query_selector_eval("h3", "e => e.innerText")
                banner = await el.query_selector_eval("img", "e => e.src")
                link = await el.query_selector("a").get_attribute("href")

                player_page = await context.new_page()
                await player_page.goto(link)
                await player_page.wait_for_timeout(5000)
                iframe = await player_page.query_selector("iframe")
                player = await iframe.get_attribute("src") if iframe else "N/A"
                await player_page.close()

                canais.append({
                    "nome": nome,
                    "banner": banner,
                    "player": player,
                    "link": link
                })

            except Exception as e:
                print("Erro:", e)

        await browser.close()
        return canais

async def salvar_firebase():
    canais = await pegar_canais()
    r = requests.put(FIREBASE_URL, data=json.dumps(canais))
    print("🔥 Firebase:", r.status_code, r.text)

asyncio.run(salvar_firebase())
