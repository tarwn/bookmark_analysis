"""
Caching content reader that cleanses HTML from tiernok.com site.

Cache occurs at both the raw HTML level and the cleansed text level,
allowing us to reduce the overhead of calling the internet and/or
re-cleansing content on every run through unless one of those methods
has changed
"""
import os.path
import codecs
import requests
from bs4 import BeautifulSoup

def is_site_text_cached(cache_folder, url, content_type):
    """
    Verifies if provided URL has already been cached in the given cache_folder
    @param cache_folder local folder cached files are kept in
    @param url Url of content to check in cache for
    @param content_type Type of cached content to look for (HTML, text)
    @return bool Whether the content is cached or not
    """
    cache_filename = create_cache_filename(cache_folder, url, content_type)
    return os.path.isfile(cache_filename) and \
           os.path.getsize(cache_filename) > 0

def create_cache_filename(cache_folder, url, content_type):
    """
    Generates a cache filename/path for a given cache folder and URL
    @param cache_folder folder cached files are kept in
    @param url URL for the content that will be cached
    @param content_type type of content (HTML or text)
    """
    cache_name = url.rsplit('/', 1)[-1]
    return os.path.join(cache_folder, "%s.%s" % (cache_name, content_type))

def cache_site_content(cache_folder, url, text, content_type):
    """
    Cache the provided site text from the given URL to the provided cache_folder
    @param cache_folder local folder cached text will be stored in
    @param url URL the provided text was downloaded from
    @param text Cleansed text to cache for the given URL
    @param content_type Type of content to cache (HTML, text)
    """
    cache_filename = create_cache_filename(cache_folder, url, content_type)
    with codecs.open(cache_filename, 'w', 'utf-8') as cache_file:
        cache_file.write(text)

def get_cached_site_content(cache_folder, url, content_type):
    """
    Returns the cached site text for the given URL from the local cache_folder
    @param cache_folder local folder cached content is stored int
    @param url remote URL that we want to load cache dtext for
    @param content_type Type of content to load from cache (HTML or text)
    @return string cached site text
    """
    cache_filename = create_cache_filename(cache_folder, url, content_type)
    with codecs.open(cache_filename, 'r', 'utf-8') as cache_file:
        return cache_file.read()

def download_site_html(url):
    """
    Downloads and cleanses the content of the specified url
    @param url URL to download content from
    @return string html content of the site
    """
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    return html

def cleanse_html(html):
    """
    Cleanse HTML into plain text
    @param html HTML string to cleanse
    @return string Text without HTML markup
    """
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find('article')
    for element in content.findAll(class_="bwp-syntax-block"):
        element.extract()
    for element in content.findAll(class_="ep-post-comments"):
        element.extract()
    for element in content.findAll(class_="ep-post-subtext"):
        element.extract()
    return content.get_text().lower()

class CacheableReader(object):
    """
    A reader that downloads and cleanses content from the web, with local caching
    based on the final segment of the URL
    """

    def __init__(self, cache_folder):
        self.cache_folder = cache_folder

    def get_site_text(self, url, force=False):
        """
        Provide cleansed text for the provided URL utilizing a read-through local cache_site_text
        @param url URL for the remote resource
        @param force Force fresh download, bypassing the local cache_site_text
        @return string Cleansed text content for the provided URL
        """

        load_html_fresh = force is True or \
                          is_site_text_cached(self.cache_folder, url, 'HTML') is False

        load_text_fresh = force is True or \
                          load_html_fresh is True or \
                          is_site_text_cached(self.cache_folder, url, 'text') is False

        if load_html_fresh is True:
            html = download_site_html(url)
            cache_site_content(self.cache_folder, url, html, 'HTML')
        else:
            html = get_cached_site_content(self.cache_folder, url, 'HTML')

        if load_text_fresh is True:
            text = cleanse_html(html)
            cache_site_content(self.cache_folder, url, text, 'text')
        else:
            text = get_cached_site_content(self.cache_folder, url, 'text')

        return text

