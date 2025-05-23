
"""Verificar se tem novas vagas em michaelpage.com.br/jobs/information-technology

As vagas são abertas no navegador.
"""

import requests
from bs4 import BeautifulSoup
import json; import itertools
from datetime import datetime
import webbrowser
import argparse
from playwright.sync_api import sync_playwright

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Check for new job postings on michaelpage.com.br/jobs/information-technology')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--open-browser', action='store_true', help='Open links in the browser')
group.add_argument('--no-browser', action='store_true', help='Do not open links in the browser')
args = parser.parse_args()

# Fetch the source code of the URL
url = 'https://www.michaelpage.com.br/jobs/information-technology?page-index=1&sort_by=min_to_max'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state()
    html_content = page.content()
    browser.close()

# Save the fetched source code to a file
with open('michaelpage.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all links from <li class="views-row"> elements
job_links = ['https://www.michaelpage.com.br' + li.find('a', class_='view-job')['href'] for li in soup.find_all('li', class_='views-row')]

# Load existing data from JSON file if it exists
try:
	with open('michaelpage.json', 'r') as file:
		existing_data = json.load(file)
except FileNotFoundError:
	existing_data = []

file_links = set(itertools.chain.from_iterable(entry['links'] for entry in existing_data))
new_links = [link for link in job_links if link not in file_links]

# Check if the last dictionary's 'links' key is not empty and verify the first element
if existing_data and 'links' in existing_data[-1] and existing_data[-1]['links']:
    last_link = existing_data[-1]['links'][0]
    if last_link not in job_links:
        raise ValueError(f"A última vaga mais recente não foi encontrada. Isso pode significar que possa existir uma segunda página de vagas em {url}.")

# Prepare data to be stored in JSON
data = {'date': datetime.now().isoformat(), 'links': new_links}
existing_data.append(data)

# Save updated data back to JSON file
with open('michaelpage.json', 'w') as file:
	json.dump(existing_data, file, indent=4)

# Print the length of the set of texts
print('Total de vagas: ', len(job_links))
print('Novas vagas: ', len(new_links))

# Open links of new job postings in a new window
if args.open_browser:
	try:
		webbrowser.open_new(list(new_links)[0])
		for text in list(new_links)[1:]:
			webbrowser.open(text)
	except IndexError:
		None
