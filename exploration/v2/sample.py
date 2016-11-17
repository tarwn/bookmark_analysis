"""Script to run through new cleanse and RAKE logic"""
import time
import contentloader
import RAKE
import os

def execute(pages):
    """Execute RAKE algorithm on each page and return top scoring phrases"""

    start_time = time.time()

    #1: Import stopwords from an external file
    rake = RAKE.Rake('stoplists/SmartStoplist.txt')

    #2: Initialize a URL reader with local caching to be kind to the internet
    rel_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')
    reader = contentloader.CacheableReader(rel_dir)

    #3: Process each file and display top keywords
    for page in pages:
        print('Processing %s' % page)
        page_text = reader.get_site_text(page)
        keywords = rake.run(page_text)
        for keyword, score in keywords[:5]:
            print('Keyword: %s, score: %d' % (keyword, score))

    end_time = time.time() - start_time
    print('Done. Elapsed: %d' % end_time)

execute([
    'http://tiernok.com/posts/continuous-javascript-test-execution-with-wallabyjs.html',
    'http://tiernok.com/posts/stop-manually-updating-your-jasmine-specrunner.html',
    'http://tiernok.com/posts/self-hosted-web-updating-assets-without-restarting-the-debugger.html',
    'http://tiernok.com/posts/asp-net-single-sign-on-against-office365-with-oauth2.html',
    'http://tiernok.com/posts/improved-teamcity-net-build-warnings.html'
])
