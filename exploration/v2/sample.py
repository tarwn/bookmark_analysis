"""Script to run through new cleanse and RAKE logic"""
import time
import contentloader
import RAKE
import os
import tfidf

def execute(pages):
    """Execute RAKE algorithm on each page and return top scoring phrases"""

    start_time = time.time()

    #1: Initialize a URL reader with local caching to be kind to the internet
    rel_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')
    reader = contentloader.CacheableReader(rel_dir)

    #2: Collect raw text for pages
    processed_pages = []
    for page in pages:
        page_text = reader.get_site_text(page)
        processed_pages.append({"url": page, "text": page_text})

    #3: RAKE keywords for each page
    rake = RAKE.Rake('stoplists/SmartStoplist.txt', min_char_length=2, max_words_length=5)
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

execute([
     'http://tiernok.com/posts/continuous-javascript-test-execution-with-wallabyjs.html',
     'http://tiernok.com/posts/stop-manually-updating-your-jasmine-specrunner.html',
     'http://tiernok.com/posts/self-hosted-web-updating-assets-without-restarting-the-debugger.html',
     'http://tiernok.com/posts/asp-net-single-sign-on-against-office365-with-oauth2.html',
     'http://tiernok.com/posts/improved-teamcity-net-build-warnings.html'
])

