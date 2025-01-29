from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import os
import requests

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 '
        'Safari/605.1.15'
}


def log(message):
    now = datetime.now(ZoneInfo('America/New_York'))
    print(now.strftime('%Y-%m-%d %H:%M:%S') + " " + message)


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/rss+xml',
            'Cache-Control': 'max-age=14400'
        },
        'body': get_feed(False)
    }


def sorter(el):
    return el["date_published"]


def get_feed(debug):
    url = os.environ.get("URL")
    log("HTTP Start " + url)
    html = requests.get(url, headers=HEADERS)
    log("HTTP End")

    if debug:
        post_file = open("data.xml", "w")
        post_file.write(html.text)
        post_file.close()

    log("Parse Start")
    page = BeautifulSoup(html.text, 'html.parser')
    log("Parse End")

    page.find('title').string.replace_with('Daily Blast+')

    oldest = datetime.now(ZoneInfo('UTC')) - timedelta(days=10)
    for article in page.find_all('item'):
        article_title = article.find('title').text
        if 'Daily Blast' not in article_title:
            article.decompose()
            continue

        # <pubDate>Tue, 28 Jan 2025 15:39:10 -0000</pubDate>
        article_date_string = article.find('pubdate').text
        article_date = datetime.strptime(article_date_string, "%a, %d %b %Y %H:%M:%S %z")
        if article_date < oldest:
            article.decompose()
            continue

        article_title = (article_title.removeprefix('The Daily Blast')
                         .removeprefix(': ').removeprefix('  - ').removeprefix(' - ').strip())
        article.find('title').string.replace_with(article_title)
        log(article_title)

    log("END")
    return page.prettify()


def test_feed():
    log('TEST START')
    debug = 'LAMBDA_NAME' not in os.environ
    feed_str = get_feed(debug)
    if debug:
        feed_file = open("feed.xml", "w")
        feed_file.write(feed_str)
        feed_file.close()
    assert ('pubdate' in feed_str)
    log('TEST END')


if __name__ == '__main__':
    test_feed()
