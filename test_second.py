"""
No VS criar o venv no termianl
python -m venv myenv

No CMD pra ativar o ambiente virtual

.\myenv\Scripts\Activate
(myenv) C:\seus\caminhos>

No VS
ctrl+shidt+p e procuro por python: select interpreter
./myenv/Scripts/python.exe

Com o ambiente a tivado
pip install alguma_coisa

"""
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import re

wordlist = ['']
target_month = int(input())
target_year = 2025

def parse_data(data_str):
    match = re.search(r'([A-Za-z]+)\s+\d{1,2},\s+\d{4}', data_str)
    if match:
        date_part = match.group()
        for fmt in ("%b %d, %Y", "%B %d, %Y", ):
            return datetime.strptime(date_part, fmt)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('', wait_until="domcontentloaded")
    results = []
    ultima_pagina_com_mes = False  

    while True:
        # Verifica news de TODOS os artigos da página
        artigos = page.query_selector_all('div.body-post')
        news = []
        
        for artigo in artigos:
                data_str = artigo.query_selector('span.h-datetime').inner_text().strip()
                data = parse_data(data_str)
                if data:
                    news.append(data)

        if all(data.month < target_month or data.year < target_year for data in news):
            print("Done.")
            break

        for artigo in artigos:

            link = artigo.query_selector('a.story-link').get_attribute('href')
            titulo = artigo.query_selector('h2.home-title').inner_text().strip()
            data_str = artigo.query_selector('span.h-datetime').inner_text().strip()
            data = parse_data(data_str)

            if not (link and titulo and data):
                continue

            if (data.month == target_month and data.year == target_year 
                and any(p.lower() in titulo.lower() for p in wordlist)):
                    
                with context.expect_page(timeout=120000) as new_page_info:
                    artigo.query_selector('a.story-link').click(modifiers=["Shift"])
                    
                article_page = new_page_info.value

                article_page.wait_for_selector('div.articlebody', state="attached", timeout=60000)
                texto = article_page.query_selector('div.articlebody').inner_text().strip()
                        
                results.append({
                    'title': titulo,
                    'date': data_str,
                    'text': texto,
                    'link': link
                })
                article_page.close()

        next_button = page.query_selector('a.blog-pager-older-link-mobile:has-text("Next Page")')
        if next_button:
            next_new_page = next_button.get_attribute('href')
            if next_new_page:
                page.goto(next_new_page, wait_until="domcontentloaded")
            else:
                break
        else:
            break

    if results:
        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    else:
        print("\nNo news have been found!")

    context.close()
    browser.close()
