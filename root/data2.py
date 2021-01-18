import string

from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from urllib import request
import csv
import urllib.request
import requests
import spacy
import os


def scrape_text(url):
    html = urllib.request.urlopen(url).read()
    if html == b'404':
        return None
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.select_one('#main > div.mr10 > p[align="justify"]')
    for i in block.select('span.fr'):
        i.decompose()
    return block.get_text()


def read_entire_file(url):
    with open(url, "r", encoding="utf-8") as fd:
        return fd.read()


def write_to_file(author, sentences, method):
    with open(f'{method}.csv', 'r', newline='', encoding='utf-8') as fd:
        row_count = sum(1 for row in fd)

    with open(f'{method}.csv', 'a', newline='', encoding='utf-8') as fd:
        csv_writer = csv.writer(fd, quoting=csv.QUOTE_ALL)
        for i, token in enumerate(sentences):
            csv_writer.writerow([i + row_count, token, author])


def get_sentences(text):
    text = ' '.join(text.split())
    sentences = sent_tokenize(text)
    return sentences


# def read_data_append_csv(author, url, method='spacy'):
#     text = read_entire_file(url)
#     print(f'Reading file {url}')
#     if method == 'lkssais':
#         text = lemmatize_text(text)
#     sent = get_sentences(text)
#     if method == 'spacy':
#         sent[:] = [lemmatize_w_spacy(s) for s in sent]
#         sent[:] = [s for s in sent if s]
#
#     fixed_text = [" ".join(sent)]
#
#     write_to_file(author, fixed_text, method)
def read_data_append_csv(author, url, method='spacy'):
    text = read_entire_file(url)
    print(f'Reading file {url}')
    if method == 'vdu':
        fixed_text = lemmatize_text(text)

    if method == 'spacy':
        sent = get_sentences(text)
        sent[:] = [lemmatize_w_spacy(s) for s in sent]
        sent[:] = [s for s in sent if s]

        fixed_text = [" ".join(sent)]

    write_to_file(author, fixed_text, method)

# def lemmatize_text(text):
#     import re
#     re.sub(r'[?!.]+', ".", text)
#     json_resp = requests.post('http://itpu.semantika.lt/Proxy/api/chains/morph', text.encode('UTF-8')).json()
#     return ' '.join([word[0][0] for word in json_resp['annotations'][1]['annotation']['msd'] if len(word) > 0])
def lemmatize_text(text):
    import re
    re.sub(r'[?!.]+', ".", text)
    form_data = {
        "tekstas": text,
        "tipas": "anotuoti",
        "pateikti": "M",
        "veiksmas": "Rezultatas puslapyje"
    }
    html_resp = requests.post('https://klc.vdu.lt/svetaine/programos/tageris/tageris.php', form_data)
    soup = BeautifulSoup(html_resp.text, 'html.parser')
    soup.select_one("form").decompose()

    final_features = []
    for text in soup.get_text().split(sep="\n"):
        if not text.startswith("<word"): continue

        match = re.search(r' type="([^,"]+)(,|")', text)
        final_features.append(match.group(1))

    return [" ".join(final_features)]


def lemmatize_w_spacy(sentence):
    # 1. Removal of Punctuation Marks
    nopunct = [char for char in sentence if char not in string.punctuation and char not in ('—', '–')]
    nopunct = ''.join(nopunct)
    nopunct = ' '.join(nopunct.split())

    # Lemmatising
    doc = nlp(nopunct)
    # string1 = ' '.join([word.lemma_ for word in doc])
    # doc = nlp(string1)
    return ' '.join([word.lemma_.lower() for word in doc if not word.is_stop])


nlp = spacy.load('lt_core_news_sm')
print('Kokį lematizavimo įrankį naudoti? {spacy, vdu}')
method = input()
if method not in ['spacy', 'vdu']:
    raise Exception('Neteisinga įvestis')
with open(f'{method}.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
    writer.writerow(["ID", "Text", "Author"])



for file in os.listdir("Savickis/"):
    if file.endswith(".txt"):
        read_data_append_csv("Savickis", os.path.join("Savickis", file), method=method)

for file in os.listdir("Zemaite/"):
    if file.endswith(".txt"):
        read_data_append_csv("Žemaitė", os.path.join("Zemaite", file), method=method)

for file in os.listdir("Aputis/"):
    if file.endswith(".txt"):
        read_data_append_csv("Aputis", os.path.join("Aputis", file), method=method)

for file in os.listdir("Grusas/"):
    if file.endswith(".txt"):
        read_data_append_csv("Grusas", os.path.join("Grusas", file), method=method)

for file in os.listdir("Ramonas/"):
    if file.endswith(".txt"):
        read_data_append_csv("Ramonas", os.path.join("Ramonas", file), method=method)

for file in os.listdir("Vienuolis/"):
    if file.endswith(".txt"):
        read_data_append_csv("Vienuolis", os.path.join("Vienuolis", file), method=method)


for file in os.listdir("Gutauskas/"):
    if file.endswith(".txt"):
        read_data_append_csv("Gutauskas", os.path.join("Gutauskas", file), method=method)