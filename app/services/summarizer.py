import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import google.generativeai as genai

genai.configure(api_key="AIzaSyCNVflqzF3wglnX3-1uc-lgjo36R89thCE")

async def summarize_text(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    await asyncio.sleep(5)  # Asynchronous sleep

    soup = BeautifulSoup(driver.page_source, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    driver.quit()

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = await asyncio.to_thread(model.generate_content, f"Summarize this text: '{text}'")

    return response.text
