from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import StringIO
from zoneinfo import ZoneInfo


import os
import requests


PAGE = 'https://newrepublic.com/podcasts/the-daily-blast-greg-sargent'
TITLE = 'Daily Blast🔒'
ICON = "https://i.scdn.co/image/ab6765630000ba8ae8bf54498e37d8fc66e985b5"
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


def tag(xml, tag_name, tag_value):
    xml.write('\n<' + tag_name + '>' + tag_value + '</' + tag_name + '>')


def tag_encoded(xml, tag_name, tag_value):
    encoded = tag_value.replace('<', '&lt;').replace('>', '&gt;').replace("\xa0", " ").strip()
    tag(xml, tag_name, encoded)


def get_feed(debug):
    url = os.environ.get("URL")

    xml = StringIO()
    xml.write("""<?xml version='1.0' encoding='UTF-8'?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
<channel>
""")
    tag(xml, 'title', TITLE)
    tag(xml, 'description', TITLE)
    tag(xml, 'link', PAGE)
    tag(xml, 'language', 'en')
    xml.write('\n<image>')
    tag(xml, 'url', ICON)
    tag(xml, 'title', TITLE)
    tag(xml, 'link', PAGE)
    xml.write('\n</image>')

    tag(xml, 'generator', 'https://github.com/prenagha/greg-sarget-rss-filter')
    tag(xml, 'itunes:block', 'yes')

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

    oldest = datetime.now(ZoneInfo('UTC')) - timedelta(days=10)
    for article in page.find_all('item'):
        article_title = article.find('title').text
        if 'Daily Blast' not in article_title:
            continue

        # <pubDate>Tue, 28 Jan 2025 15:39:10 -0000</pubDate>
        article_date_string = article.find('pubdate').text
        article_date = datetime.strptime(article_date_string, "%a, %d %b %Y %H:%M:%S %z")
        if article_date < oldest:
            continue

        article_title = (article_title.removeprefix('The Daily Blast')
                         .removeprefix(': ').removeprefix('  - ').removeprefix(' - ').strip())
        article.find('title').string.replace_with(article_title)
        log(article_title)

        guid = article.find('guid').text
        enclosure = article.find('enclosure')
        mp3_url = enclosure.get('url')
        mp3_type = enclosure.get('type')
        mp3_length = enclosure.get('length')

        xml.write('\n\n<item>')
        tag_encoded(xml, 'title', article_title)
        tag_encoded(xml, 'description', article.find('content:encoded').text)
        xml.write('\n<guid isPermaLink="false">' + guid + '</guid>')
        tag(xml, 'pubDate', article_date.strftime("%a, %d %b %Y %H:%M:%S %z"))
        xml.write('\n<enclosure url="' + mp3_url + '" length="' + mp3_length + '" type="' + mp3_type + '"/>')
        xml.write('\n</item>')

    log("END")
    return xml.getvalue() + '\n\n</channel>\n</rss>\n'


def test_feed():
    log('TEST START')
    debug = 'LAMBDA_NAME' not in os.environ
    feed_str = get_feed(debug)
    if debug:
        feed_file = open("feed.xml", "w")
        feed_file.write(feed_str)
        feed_file.close()
    assert ('pubDate' in feed_str)
    log('TEST END')


if __name__ == '__main__':
    test_feed()
