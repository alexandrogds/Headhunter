
"""Verificar se tem novas vagas em michaelpage.com.br/jobs/information-technology

As vagas são abertas no navegador.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import webbrowser

# Fetch the source code of the URL
url = 'https://www.michaelpage.com.br/jobs/information-technology'
response = requests.get(url)
html_content = response.content

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all texts of <em> tags and put them in a set
em_texts = set(em.get_text() for em in soup.find_all('em'))

# Load existing data from JSON file if it exists
try:
	with open('michaelpage.json', 'r') as file:
		existing_data = json.load(file)
except FileNotFoundError:
	existing_data = []

# Ensure no duplicate texts in JSON
# all_texts = set()
# for lst in existing_data:
# 	for entry in lst:
# 		all_texts.update(entry['link'])
all_texts = set()
for entry in existing_data:
	all_texts.add(entry['link'])

new_texts = em_texts - all_texts

# Prepare data to be stored in JSON
data = []
for text in new_texts:
	aux = {
		'date': datetime.now().isoformat(),
		'link': text
	}
	data += [aux]

# Append new data to existing data
existing_data += data

# Save updated data back to JSON file
with open('ccrh.json', 'w') as file:
	json.dump(existing_data, file, indent=4)

# Print the length of the set of texts
print('Total de vagas: ', len(em_texts))
print('Novas vagas: ', len(new_texts))

# Open links of new job postings in a new window
try:
	webbrowser.open_new(list(new_texts)[0])
	for text in list(new_texts)[1:]:
		webbrowser.open(text)
except IndexError:
	None