import json
import requests
from io import StringIO
from lxml import etree
from lxml.html import parse
from urllib.request import urlopen

class Youtube():
    def __init__(self):
        pass

    @staticmethod
    def video_id(string):
        return string[9:20] if "watch" in string else string

    @classmethod
    def count_youtube_playlist(cls, url):
        return len(list(cls.scrap_playlist(url)))

    @staticmethod
    def get_yt_playlist_title(url):
        page = urlopen(url)
        p = parse(page)
        playlist_title = p.find("//meta[@name='title']").attrib['content']
        return playlist_title[:-10]  # Quitar la parte de " - YouTube"

    @classmethod
    def scrap_playlist(cls, url):
        mostrar_mas = None
        r = requests.get(url)
        parser = etree.HTMLParser()
        if "browse_ajax" in r.url:
            rd = json.loads(r.text)
            tree = etree.parse(StringIO(rd['content_html']), parser)
            mostrar_mas = etree.parse(StringIO(rd['load_more_widget_html']), parser).xpath('//@data-uix-load-more-href')[0] if rd.get('load_more_widget_html') else None
            lista_videos = tree.xpath('//a[contains(@class, "pl-video")]')

        else:
            tree = etree.parse(StringIO(r.text), parser)
            mostrar_mas = tree.xpath('//button//@data-uix-load-more-href')[0] if tree.xpath('//button//@data-uix-load-more-href') else None
            lista_videos = tree.xpath('//a[contains(@class, "pl-video-title-link")]')

        for vid in lista_videos:
            yield {'youtube_id': cls.video_id(vid.attrib['href']), 'name': str(vid.text.strip())}

        if mostrar_mas:
            url_mostrarmas = 'https://www.youtube.com'+mostrar_mas
            yield from cls.scrap_playlist(url_mostrarmas)
