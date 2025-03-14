"""Verificar se tem novas vagas em hays.com.br

As vagas são abertas no navegador.

hays.py=abrir a pagina de vaga diversas vezes e 
clicar no botão apropriado; abrir duas paginas de cada
"""

from bs4 import BeautifulSoup
import json; import itertools
from datetime import datetime
import webbrowser
import argparse
from playwright.sync_api import sync_playwright

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Check for new job postings on hays.com.br')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--open-browser', action='store_true', help='Open links in the browser')
group.add_argument('--no-browser', action='store_true', help='Do not open links in the browser')
args = parser.parse_args()

# Fetch the source code of the URL using Playwright to wait for JavaScript to load
url = 'https://www.hays.com.br/empregos-pesquisar'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    
    # Scroll down until the last number matches the target number
    target_number = 33
    while True:
        page.keyboard.press("PageDown")
        page.wait_for_timeout(1000)  # Wait for the page to load new content
        # Get all 'span.font-weight-bold' elements and concatenate their text
        all_span_texts = ''.join([span.inner_text() for span in page.query_selector_all('span.font-weight-bold')])
        last_number = int(all_span_texts.split()[-1])
        # Check if last_number is echoic
        len_last_number = len(str(last_number))
        if len_last_number % 2 == 0:
            if str(last_number)[:len_last_number // 2] == str(last_number)[len_last_number // 2:]:
                break
    
    # Select the option to sort by date
    page.select_option('select#gtm_sort_by', 'PUBLISHED_DATE_DESC')
    
    # Click all specified <button> elements
    buttons = page.query_selector_all('button.job-card.job-card--list.is-active.d-block.rounded-lg.pt-6.pb-5.px-6')
    
    html_content = page.content()
    browser.close()

# Save the fetched source code to a file
with open('hays.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all href attributes of specified <div> elements in order
job_links = [a['href'] for a in soup.select('div.job-tile a.view-job')]

# Load existing data from JSON file if it exists
try:
    with open('hays.json', 'r') as file:
        existing_data = json.load(file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    existing_data = []

# Ensure no duplicate links in JSON
all_links = set(itertools.chain.from_iterable(entry['links'] for entry in existing_data))
new_links = [link for link in job_links if link not in all_links]

# Check if the last dictionary's 'links' key is not empty and verify the first element
if existing_data and 'links' in existing_data[-1] and existing_data[-1]['links']:
    last_link = existing_data[-1]['links'][0]
    if last_link not in job_links:
        raise ValueError(f"A última vaga mais recente não foi encontrada. Isso pode significar que possa existir uma segunda página de vagas em {url}.")

# Prepare data to be stored in JSON
data = {'date': datetime.now().isoformat(), 'links': new_links}

# Append new data to existing data
existing_data.append(data)

# Save updated data back to JSON file
with open('hays.json', 'w') as file:
    json.dump(existing_data, file, indent=4)

# Print the length of the set of links
print('Total de vagas: ', len(job_links))
print('Novas vagas: ', len(new_links))

# Open links of new job postings in a new window if enabled
if args.open_browser:
    try:
        webbrowser.open_new(new_links[0])
        for link in new_links[1:]:
            webbrowser.open(link)
    except IndexError:
        pass
