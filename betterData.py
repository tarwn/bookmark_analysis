import requests
import RAKE
import time
from bs4 import BeautifulSoup
import math
from textblob import TextBlob as tb

pages = [
    'http://tiernok.com/posts/continuous-javascript-test-execution-with-wallabyjs.html',
    'http://tiernok.com/posts/stop-manually-updating-your-jasmine-specrunner.html',
    'http://tiernok.com/posts/self-hosted-web-updating-assets-without-restarting-the-debugger.html',
    'http://tiernok.com/posts/asp-net-single-sign-on-against-office365-with-oauth2.html',
    'http://tiernok.com/posts/improved-teamcity-net-build-warnings.html'
]

start_time = time.time()

# from http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tdidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

#end from

# 1: Method to get content of site using requests and html2test
def get_site_text(url):
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find('article')
    for element in content.findAll(class_="bwp-syntax-block"):
        element.extract()
    for element in content.findAll(class_="ep-post-comments"):
        element.extract()
    for element in content.findAll(class_="ep-post-subtext"):
        element.extract()
    return content.get_text().lower()

#2: Import stopwords from an external file
Rake = RAKE.Rake('stoplists/SmartStoplist.txt')

#3: Process each file into raw content
processed_pages = []
for page in pages:
    print('Processing %s' % page)
    page_text = get_site_text(page)
    processed_pages.append({"url": page, "raw": page_text })

#4: Generate Rake keywords
for page in processed_pages:
    keywords = Rake.run(page["raw"])
    page["rake_keywords"] = keywords[:5]

#5: Generate TF-IDF keywords
def score_page(blob, blobs):
    scores = {word: tdidf(word, blob, blobs) for word in blob.words if len(word) > 2}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

for page in processed_pages:
    page["blob"] = tb(page["raw"])

for page in processed_pages:
    page_scores = score_page(page["blob"], [page["blob"] for page in processed_pages])
    page["tfidf_keywords"] = page_scores[:5]

#6: Display results
for page in processed_pages:
    print("Page %s" % page["url"])
    print("    TF-IDF Keywords:")
    for word, score in page["tfidf_keywords"]:
        print("        Word: {}, TF-IDF: {}".format(word, round(score, 5)))
    print("    RAKE Keywords:")
    for keyword, score in page["rake_keywords"]:
        print('        Keyword: %s, score: %d' % (keyword, score))

end_time = time.time() - start_time
print('Done. Elapsed: %d' % end_time)
