"""Script to run through new cleanse and RAKE logic"""
import os
import time
import requests
from bs4 import BeautifulSoup
import contentloader
import RAKE
import tfidf

RAKE_STOPLIST = 'stoplists/SmartStoplist.txt'
CACHE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')

def execute(cleanse_method, pages):
    """Execute RAKE and TF-IDF algorithms on each page and output top scoring phrases"""

    start_time = time.time()

    #1: Initialize a URL reader with local caching to be kind to the internet
    reader = contentloader.CacheableReader(CACHE_FOLDER, cleanse_method)

    #2: Collect raw text for pages
    processed_pages = []
    for page in pages:
        page_text = reader.get_site_text(page)
        processed_pages.append({"url": page, "text": page_text})

    #3: RAKE keywords for each page
    rake = RAKE.Rake(RAKE_STOPLIST, min_char_length=2, max_words_length=5)
    for page in processed_pages:
        page["rake_results"] = rake.run(page["text"])

    #4: TF-IDF keywords for processed text
    document_frequencies = {}
    document_count = len(processed_pages)
    for page in processed_pages:
        page["tfidf_frequencies"] = tfidf.get_word_frequencies(page["text"])
        for word in page["tfidf_frequencies"]:
            document_frequencies.setdefault(word, 0)
            document_frequencies[word] += 1

    sortby = lambda x: x[1]["score"]
    for page in processed_pages:
        for word in page["tfidf_frequencies"].items():
            word_frequency = word[1]["frequency"]
            docs_with_word = document_frequencies[word[0]]
            word[1]["score"] = tfidf.calculate(word_frequency, document_count, docs_with_word)

        page["tfidf_results"] = sorted(page["tfidf_frequencies"].items(), key=sortby, reverse=True)

    #5. Results
    for page in processed_pages:
        print("-------------------------")
        print("URL: %s" % page["url"])
        print("RAKE:")
        for result in page["rake_results"][:5]:
            print(" * %s" % result[0])
        print("TF-IDF:")
        for result in page["tfidf_results"][:5]:
            print(" * %s" % result[0])

    end_time = time.time() - start_time
    print('Done. Elapsed: %d' % end_time)

def cleanse_tiernok_html(html):
    """Cleanse function for tiernok.com blog posts"""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find('article')
    for element in content.findAll(class_="bwp-syntax-block"):
        element.extract()
    for element in content.findAll(class_="ep-post-comments"):
        element.extract()
    for element in content.findAll(class_="ep-post-subtext"):
        element.extract()
    return content.get_text() \
                  .lower() \
                  .replace('\n','') \
                  .replace('\r','')

# get links because I'm too lazy to copy/pasta
resp = requests.get('http://tiernok.com/posts/index.html')
resp.raise_for_status()
html = resp.text
soup = BeautifulSoup(html, "html.parser")
anchors = soup.findAll(class_="ep-archive-title-link")
post_links = ["http://tiernok.com/posts/{0}".format(link['href'][2:]) for link in anchors]
# run algorithms
execute(cleanse_tiernok_html, post_links)
