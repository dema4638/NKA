import string

from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from urllib import request
import csv
import urllib.request
import requests
import spacy

def scrape_text(url):
    html = urllib.request.urlopen(url).read()
    if html == b'404':
        return None
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.select_one('#main > div.mr10 > p[align="justify"]')
    for i in block.select('span.fr'):
        i.decompose()
    return block.get_text()


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


def read_data_append_csv(author, url, page_limit=10000, method='spacy'):
    i = 1
    full_url = url + str(i)
    text = scrape_text(full_url)
    while text is not None and i <= page_limit:
        print(f'Scraping {full_url}')
        if method == 'lkssais':
            text = lemmatize_text(text)
        sent = get_sentences(text)
        if method == 'spacy':
            sent[:] = [lemmatize_w_spacy(s) for s in sent]
            sent[:] = [s for s in sent if s]

        write_to_file(author, sent, method)
        i += 1
        full_url = url + str(i)
        text = scrape_text(full_url)


def lemmatize_text(text):
    import re
    re.sub(r'[?!.]+', ".", text)
    json_resp = requests.post('http://itpu.semantika.lt/Proxy/api/chains/morph', text.encode('UTF-8')).json()
    return ' '.join([word[0][0] for word in json_resp['annotations'][1]['annotation']['msd'] if len(word) > 0])


def lemmatize_w_spacy(sentence):
    # 1. Removal of Punctuation Marks
    nopunct = [char for char in sentence if char not in string.punctuation]
    nopunct = ''.join(nopunct)
    nopunct = ' '.join(nopunct.split())

    # Lemmatising
    doc = nlp(nopunct)
    # string1 = ' '.join([word.lemma_ for word in doc])
    # doc = nlp(string1)
    return ' '.join([word.lemma_.lower() for word in doc if not word.is_stop])


nlp = spacy.load('lt_core_news_sm')
print('Kokį lematizavimo įrankį naudoti? {spacy, lkssais}')
method = input()
if method not in ['spacy', 'lkssais']:
    raise Exception('Neteisinga įvestis')
with open(f'{method}.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
    writer.writerow(["ID", "Text", "Author"])
read_data_append_csv("Putinas", "http://antologija.lt/text/vincas-mykolaitis-putinas-altoriu-sesely/", page_limit=18, method=method)
read_data_append_csv("Škėma", "http://antologija.lt/text/antanas-skema-balta-drobule/", page_limit=17, method=method)
read_data_append_csv("Žemaitė", "http://antologija.lt/text/zemaite-laime-nutekejimo/", method=method)
read_data_append_csv("Šatrijos ragana", "http://antologija.lt/text/satrijos-ragana-sename-dvare/",page_limit=13, method=method)
