"""Verificar se tem novas vagas em vagas.com.br

As vagas são abertas no navegador.
"""

from bs4 import BeautifulSoup
import json; import itertools
from datetime import datetime
import webbrowser
import argparse
from playwright.sync_api import sync_playwright

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Check for new job postings on vagas.com.br')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--open-browser', action='store_true', help='Open links in the browser')
group.add_argument('--no-browser', action='store_true', help='Do not open links in the browser')
args = parser.parse_args()

# Fetch the source code of the URL using Playwright to wait for JavaScript to load
url = 'https://www.vagas.com.br/vagas-de-?m%5B%5D=100%25+Home+Office&pcd%5B%5D=T&mo%5B%5D=Pessoa+Jur%C3%ADdica'
# # URL de testes com vagas +pcd -pj
# url = 'https://www.vagas.com.br/vagas-de-?m%5B%5D=100%25+Home+Office&pcd%5B%5D=T'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state()
    html_content = page.content()
    browser.close()

# Save the fetched source code to a file
with open('vagas.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract the URL from the specified <article> element
articles = soup.find_all('a', {'class': 'link-detalhes-vaga'})
job_links = [article['href'] for article in articles]

# Load existing data from JSON file if it exists
try:
    with open('vagas.json', 'r') as file:
        existing_data = json.load(file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    existing_data = []

# Ensure no duplicate links in JSON
all_links = set(itertools.chain.from_iterable(entry['links'] for entry in existing_data))
new_links = ['https://www.vagas.com.br/' + link for link in job_links if link not in all_links]

# Check if the last dictionary's 'links' key is not empty and verify the first element
if existing_data and 'links' in existing_data[-1] and existing_data[-1]['links']:
    last_link = existing_data[-1]['links'][0]
    if last_link not in job_links:
        raise ValueError(f"A última vaga mais recente não foi encontrada. Isso pode significar que possa existir uma segunda página de vagas em {url}.")

# Prepare data to be stored in JSON
data = {'date': datetime.now().isoformat(), 'links': new_links}
existing_data.append(data)

# Save updated data back to JSON file
with open('vagas.json', 'w') as file:
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
