
"""Verificar se tem novas vagas em jobs.quickin.io/evtit

As vagas são abertas no navegador.
"""

import json; import itertools
from datetime import datetime
import argparse; import time
import webbrowser
from playwright.sync_api import sync_playwright

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Check for new job postings on jobs.quickin.io/evtit')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--open-browser', action='store_true', help='Open links in the browser')
group.add_argument('--no-browser', action='store_true', help='Do not open links in the browser')
args = parser.parse_args()

# Fetch the source code of the URL using Playwright to wait for JavaScript to load
url = 'https://jobs.quickin.io/evtit/jobs?title=&position_category=it'

with sync_playwright() as p:
	browser = p.chromium.launch()
	page = browser.new_page()
	page.goto(url)
	page.wait_for_load_state()
	
	# Define next_page_items
	next_page_items = page.query_selector_all('li.page-item a.page-link')
	
	job_links = []
	for item in next_page_items:
		item.click()
		page.wait_for_load_state()
		time.sleep(1)
		
		# Get job links
		job_rows = page.query_selector_all('tr[data-v-4491386a] a.text-dark')
		job_links += [row.get_attribute('href') for row in job_rows]
	
	browser.close()

# Remove duplicate job_links while maintaining order
unique_job_links = []
seen = set()
for link in job_links:
	if link not in seen:
		unique_job_links.append(link)
		seen.add(link)

job_links = unique_job_links

# Load existing data from JSON file if it exists
try:
	with open('quickin.json', 'r') as file:
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
existing_data.append(data)

# Save updated data back to JSON file
with open('quickin.json', 'w') as file:
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
