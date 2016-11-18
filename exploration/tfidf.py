import requests
import html2text
import math
from textblob import TextBlob as tb
import time

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

# 1: Get content of site using requests and html2test
def get_site_text(url):
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    return html2text.html2text(html)

# 2: Score each word for an individual page against the full set of pages
def score_page(blob, blobs):
    scores = {word: tdidf(word, blob, blobs) for word in blob.words if len(word) > 2}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# 3: For each URL in the page list, get the text content and a TextBlob for the content
completed_pages = []
for page in pages:
    print('Processing %s' % page)
    try:
        raw = get_site_text(page).lower()
        completed_pages.append({"page": page, "raw": raw, "blob": tb(raw)})
    except Exception as exc:
        print('Couldn\'t download %s, error: %s' % (page, exc))
        continue

# 4: For each page, calculate TF-IDF scores and output top 5 scoring words
for page in completed_pages:
    print('Scoring %s' % page["page"])
    page_scores = score_page(page["blob"], [page["blob"] for page in completed_pages])
    for word, score in page_scores[:5]:
        print("\rWord: {}, TF-IDF: {}".format(word, round(score, 5)))

end_time = time.time() - start_time
print('Done. Elapsed: %d' % end_time)
