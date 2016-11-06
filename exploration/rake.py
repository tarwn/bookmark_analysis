import requests
import html2text
import RAKE
import time

pages = [
    'http://tiernok.com/posts/continuous-javascript-test-execution-with-wallabyjs.html',
    'http://tiernok.com/posts/stop-manually-updating-your-jasmine-specrunner.html',
    'http://tiernok.com/posts/self-hosted-web-updating-assets-without-restarting-the-debugger.html',
    'http://tiernok.com/posts/asp-net-single-sign-on-against-office365-with-oauth2.html',
    'http://tiernok.com/posts/improved-teamcity-net-build-warnings.html'
]

start_time = time.time()

# 1: Method to get content of site using requests and html2test
def get_site_text(url):
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    return html2text.html2text(html)

#2: Import stopwords from an external file
Rake = RAKE.Rake('stoplists/SmartStoplist.txt')

#3: Process each file and display top keywords
for page in pages:
    print('Processing %s' % page)
    page_text = get_site_text(page)
    keywords = Rake.run(page_text)
    for keyword, score in keywords[:5]:
        print('Keyword: %s, score: %d' % (keyword, score))

end_time = time.time() - start_time
print('Done. Elapsed: %d' % end_time)
