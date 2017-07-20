import re
import os
import json
import uuid
import glob
import shutil
import zipfile
import requests
import datetime
from io import StringIO
from lxml import etree
from lxml.html import parse
from urllib.request import urlopen

def remove_special_characters(s):
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        if ch in s:
            s = s.replace(ch, "")
    return s

def get_yt_playlist_title(url):
    page = urlopen(url)
    p = parse(page)
    playlist_title = p.find("//meta[@name='title']").attrib['content']
    return playlist_title[:-10]  # Quitar la parte de " - YouTube"

def get_playlist_source(url):
    # Hacer bien esta funcion
    return 'Spotify' if 'spot' in url else 'YouTube'

def get_sp_playlist_data(url):
    user = re.search(r'(?<=user\/|user:)(.*)(?=\/playlist|:playlist)', url).group(0)
    idplaylist = re.search(r'(?<=playlist\/|playlist:)(.*)', url).group(0)
    return {'user': user, 'idplaylist': idplaylist}

def gen_uuid():
    return str(uuid.uuid4())

def video_id(string):
    return string[9:20] if "watch" in string else string

def create_dir(dirname):
    if not os.path.exists(dirname):
            os.makedirs(dirname)
            return True
    list(map(os.unlink, (os.path.join(dirname, f) for f in os.listdir(dirname))))
    return True

def delete_files(dirname):
    files = glob.glob('{}/*'.format(dirname))
    for f in files:
        os.remove(f)

def delete_folder(dirname):
    shutil.rmtree(dirname)

def calculate_time_left(total, c, start_time):
    """ Progress bar time left  """
    fraction_done = c / total
    est_time_left = 0
    if fraction_done > 0:
        est_time_left = ((1 - fraction_done) / fraction_done) * ((start_time - datetime.datetime.now()).total_seconds())
    else:
        est_time_left = 0
    return [(fraction_done * 100), abs(est_time_left)]

def create_zip(file_name, folder_path):
    zipf = zipfile.ZipFile('{}.zip'.format(file_name), 'w', zipfile.ZIP_DEFLATED)
    # ziph is zipfile handle
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zipf.write(os.path.join(root, file), file)
    zipf.close()

def count_youtube_playlist(url):
    return len(list(scrap_youtube_playlist(url)))

def youtube_playlist_data(url):
    return {
        'name': get_yt_playlist_title(url),
        'url': url,
        'source': get_playlist_source(url),
    }

def scrap_youtube_playlist(url):
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
        yield {'youtube_id': video_id(vid.attrib['href']), 'name': str(vid.text.strip())}

    if mostrar_mas:
        url_mostrarmas = 'https://www.youtube.com'+mostrar_mas
        yield from scrap_youtube_playlist(url_mostrarmas)
