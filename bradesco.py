"""Verificar se tem novas vagas em michaelpage.com.br/jobs/information-technology

As vagas são abertas no navegador.
"""

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

asks = ['remot', 'home', 'pj', 'pcd']

with sync_playwright() as p:
	for ask in asks:
		url = f'https://bradesco.csod.com/ux/ats/careersite/1/home?c=bradesco&sq={ask}'
		browser = p.chromium.launch()
		page = browser.new_page()
		page.goto(url)
		page.wait_for_selector('div.p-panel.p-bg-white.p-p-md.p-bw-xs.p-bc-grey70.p-bs-solid.rounded-all')
		html_content = page.content()

		# Save the fetched source code to a file
		with open(f'bradesco/{ask}.html', 'w', encoding='utf-8') as file:
			file.write(html_content)

		# Parse the HTML content
		soup = BeautifulSoup(html_content, 'html.parser')

		# # Get all text from the specified <p> elements
		# job_titles = [p.get_text() for p in soup.select('p.p-text.p-f-sz-md.p-t-primary50.p-f-w-6')]

		# # Get all text from the specified <p> elements for job posting dates
		# job_dates = [p.get_text() for p in soup.select('p.p-text.p-f-sz-xs.p-t-muted.p-f-w-n.p-t-wr-fw')]

		# Get all text from the specified <div> elements
		job_details = [div.get_text() for div in soup.select('div.p-panel.p-bg-white.p-p-md.p-bw-xs.p-bc-grey70.p-bs-solid.rounded-all')]

		# Load existing data from JSON file if it exists
		try:
			with open(f'bradesco/{ask}.json', 'r') as file:
				existing_data = json.load(file)
		except (FileNotFoundError, json.decoder.JSONDecodeError):
			existing_data = []

		# Ensure no duplicate links in JSON
		all_details = set(itertools.chain.from_iterable(entry['details'] for entry in existing_data))
		all_dates = [entry['date'] for entry in existing_data]
		new_details = [detail for detail in job_details if detail not in all_details]

		# # Check if the last dictionary's 'links' key is not empty and verify the first element
		# if existing_data and 'links' in existing_data[-1] and existing_data[-1]['links']:
		# 	last_link = existing_data[-1]['links'][0]
		# 	if last_link not in job_links:
		# 		raise ValueError(f"A última vaga mais recente não foi encontrada. Isso pode significar que possa existir uma segunda página de vagas em {url}.")

		data = {'date': datetime.now().isoformat(), 'details': new_details}
		existing_data.append(data)

		# # Group the links by the same dates
		# grouped_data = {}
		# for date, link in zip(new_dates, new_links):
		# 	if date not in grouped_data:
		# 		grouped_data[date] = []
		# 	grouped_data[date].append(link)

		# # Prepare data to be stored in JSON
		# for date, links in grouped_data.items():
		# 	data = {'date': date, 'links': links}
		# 	existing_data.append(data)

		# Save updated data back to JSON file
		with open(f'bradesco/{ask}.json', 'w') as file:
			json.dump(existing_data, file, indent=4)

		# Print the length of the set of links
		print(f'Busca por: {ask}')
		print('Total de vagas:', len(job_details))
		print('Novas vagas:', len(new_details))
		print('Última verificação:', all_dates[-1], end='\n\n')

		# Open links of new job postings in a new window if enabled
		if args.open_browser:
			if new_details:
				webbrowser.open_new(url)

		browser.close()
