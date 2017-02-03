import requests
import json
import re
import os
import uuid
import datetime
import glob
import zipfile
from io import StringIO
from lxml import etree
from lxml.html import parse
from urllib.request import urlopen
import utils.youtubemp3 as YTMP3

def get_yt_playlist_title(url):
    page = urlopen(url)
    p = parse(page)
    playlist_title = p.find("//meta[@name='title']").attrib['content']
    return playlist_title

def get_sp_playlist_data(url):
    user = re.search(r'(?<=user\/|user:)(.*)(?=\/playlist|:playlist)', url).group(0)
    idplaylist = re.search(r'(?<=playlist\/|playlist:)(.*)', url).group(0)
    return {'user': user, 'idplaylist': idplaylist}

def gen_uuid():
    return str(uuid.uuid4())

def video_id(string):
    return string[9:20] if "watch" in string else string

def prepare_string_for_file(string):
    string = string.strip()
    string = re.sub(r'\[.*?\]', '', string)
    return re.sub(r'[^a-zA-ZñÑ0-9\-\ ]', '', string)

def crate_dir(dirname):
    if not os.path.exists(dirname):
            os.makedirs(dirname)
            return True
    return False

def delete_files(dirname):
    files = glob.glob('{}/*'.format(dirname))
    for f in files:
        os.remove(f)

def calculate_time_left(total, c, start_time):
    """ Progress bar time left  """
    fraction_done = c / total
    est_time_left = 0
    if fraction_done > 0:
        est_time_left = ((1 - fraction_done) / fraction_done) * ((start_time - datetime.datetime.now()).total_seconds())
    else:
        est_time_left = 0
    return [(fraction_done * 100), abs(est_time_left)]

def create_zip(file_name, folder_uuid):
    zipf = zipfile.ZipFile('{}.zip'.format(file_name), 'w', zipfile.ZIP_DEFLATED)
    # ziph is zipfile handle
    for root, dirs, files in os.walk(folder_uuid):
        for file in files:
            zipf.write(os.path.join(root, file), file)
    zipf.close()

def count_youtube_playlist(url):
    return len(list(scrap_youtube_playlist_anon(url)))

def count_spotify_playlist(token, spotify_user, listaid):
    return len(list(YTMP3.get_sp_tracknames(token=token, user=spotify_user, listaid=listaid)))

def scrap_youtube_playlist_anon(url):
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
        yield [video_id(vid.attrib['href']), str(vid.text.strip())]

    if mostrar_mas:
        url_mostrarmas = 'https://www.youtube.com'+mostrar_mas
        yield from scrap_youtube_playlist_anon(url_mostrarmas)
