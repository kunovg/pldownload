# -*- coding: utf-8 -*-
import eventlet
import json
from platforms.spotify import Spotify
from platforms.youtube import Youtube
import utils.utils as UTILS
import utils.pwsecurity as PWS
import utils.downloaders as Downloaders
import sql.user as USER
import sql.playlist as PLAYLIST
from queue import Queue
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, request, send_file, render_template

eventlet.monkey_patch()  # Resuelve el emit dentro de threads
app = Flask(__name__)
CORS(app)
socket = SocketIO(app)
DIRECTORY, SPOTIFY, linksqueue, idsqueue = None, None, None, None
config = json.load(open("config.json", "r"))

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/user/create', methods=['POST'])
def insert_user():
    user = request.json
    user['password'] = PWS.hash(user['password'])
    USER.create_user(user=user)
    return json.dumps(True)

@app.route('/playlist/create', methods=['POST'])
def insert_playlist():
    r = request.json
    url = r.get('url')
    source = UTILS.get_playlist_source(url)
    if source == 'YouTube':
        songs = list(Youtube.scrap_youtube_playlist(url))
        name = Youtube.get_yt_playlist_title(url)
    elif source == 'Spotify':
        user, idplaylist = Spotify.get_user_and_id(url)
        songs = SPOTIFY.scrap_spotify_playlist(user, idplaylist)
        name = SPOTIFY.get_sp_tracklist_name(url)
    res = PLAYLIST.create_playlist(
        user_id=request.headers.get('User'),
        playlist=dict(source=source, url=url, name=name),
        songs=songs)
    return json.dumps(res)

@app.route('/playlist/update', methods=['POST'])
def update_playlist():
    r = request.json
    source, url, songs = r.get('source'), r.get('url'), None
    playlist_id, user_id = r.get('id'), request.headers.get('User')
    if source == 'YouTube':
        songs = list(Youtube.scrap_youtube_playlist(url))
    elif source == 'Spotify':
        user, idplaylist = Spotify.get_user_and_id(url)
        songs = SPOTIFY.scrap_spotify_playlist(user, idplaylist)
    assert songs
    res = PLAYLIST.update_playlist(
        playlist_id,
        user_id=user_id,
        songs=songs)
    return json.dumps(res)

@app.route('/playlist/unlink', methods=['POST'])
def unlink_playlist():
    r = request.json
    playlist_id, user_id = r.get('id'), request.headers.get('User')
    return json.dumps(PLAYLIST.unlink_playlist(user_id, playlist_id))

@app.route('/validate', methods=['POST'])
def validate():
    attr, name = list(request.json.items())[0]
    return json.dumps(USER.valid(attr, name))

@app.route('/login', methods=['POST'])
def login():
    _id = USER.valid_password(
        password=request.json['password'],
        name=request.json['name'])
    if _id:
        return json.dumps(USER.get_basic_info(_id))
    return ('', 400)

@app.route('/playlists', methods=['GET'])
def get_playlists():
    user_id = request.args.get('userId')
    return json.dumps(USER.get_playlists(user_id))

@app.route('/fulldownload', methods=['POST'])
def fulldownload():
    def finished_download_callback(user_id, playlist_id, uuid, songs_id, tipo):
        PLAYLIST.update_last_date_type(playlist_id, user_id, tipo)
        PLAYLIST.add_downloaded(user_id, playlist_id, songs_id=songs_id)
        print('emit1')
        socket.emit(str(user_id), dict(playlist_id=playlist_id, uuid=uuid, status='finished'), broadcast=True)
        print('emit2')

    playlist_id = request.json['playlistId']
    user_id = request.headers.get('User')

    # Mandar mensaje de descarga iniciada
    socket.emit(str(user_id), dict(playlist_id=playlist_id, status='started', c=0, t=1), broadcast=True)

    playlist = PLAYLIST.get_playlist_information(playlist_id, user_id)
    playlist_queue = Queue()
    playlist_path = DIRECTORY + playlist['uuid']
    UTILS.create_dir(playlist_path)
    length = len(playlist['songs'])
    for s, i in zip(playlist['songs'], range(length)):
        idsqueue.put({
            **s,
            'c': i,
            'total': length,
            'user_id': user_id,
            'linksqueue': linksqueue,
            'playlist_id': playlist_id,
            'playlist_path': playlist_path,
            'playlist_queue': playlist_queue,
            'playlist_name': playlist.get('name'),
            'song_download_callback': lambda c, t: socket.emit(str(user_id), dict(c=c, t=t, playlist_id=playlist_id, status='downloading'), broadcast=True),
            'finished_download_callback': lambda songs_id: finished_download_callback(user_id=user_id, playlist_id=playlist_id, uuid=playlist.get('uuid'), songs_id=songs_id, tipo='Full'),
        })
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/partialdownload', methods=['POST'])
def partialdownload():
    def finished_download_callback(user_id, playlist_id, uuid, songs_id, tipo):
        PLAYLIST.update_last_date_type(playlist_id, user_id, tipo)
        PLAYLIST.add_downloaded(user_id, playlist_id, songs_id=songs_id)
        socket.emit(str(user_id), dict(playlist_id=playlist_id, uuid=uuid, status='finished'), broadcast=True)

    playlist_id = request.json['playlistId']
    user_id = request.headers.get('User')

    # Mandar mensaje de descarga iniciada
    socket.emit(str(user_id), dict(playlist_id=playlist_id, status='started', c=0, t=1), broadcast=True)

    playlist = PLAYLIST.get_playlist_information(playlist_id, user_id)
    playlist_queue = Queue()
    playlist_path = DIRECTORY + playlist['uuid']
    UTILS.create_dir(playlist_path)
    songs = [s for s in playlist['songs'] if s['id'] not in playlist['downloaded']]
    length = len(songs)
    for s, i in zip(songs, range(length)):
        idsqueue.put({
            **s,
            'c': i,
            'total': length,
            'user_id': user_id,
            'linksqueue': linksqueue,
            'playlist_id': playlist_id,
            'playlist_path': playlist_path,
            'playlist_queue': playlist_queue,
            'playlist_name': playlist.get('name'),
            'song_download_callback': lambda c, t: socket.emit(str(user_id), dict(c=c, t=t, playlist_id=playlist_id, status='downloading'), broadcast=True),
            'finished_download_callback': lambda songs_id: finished_download_callback(user_id=user_id, playlist_id=playlist_id, uuid=playlist.get('uuid'), songs_id=songs_id, tipo='Partial'),
        })
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/get', methods=['GET'])
def get_file():
    return send_file(
        as_attachment=True,
        mimetype="application/zip",
        filename_or_fp="{}{}.zip".format(DIRECTORY, request.args.get('uuid')))

if __name__ == "__main__":
    DIRECTORY = config['file_directory']
    SPOTIFY = Spotify(config['spotify_token'])
    SPOTIFY.get_sp_token()
    linksqueue, idsqueue = Queue(), Queue()
    for x in range(config['scrapper_workers']):
        scrapper = Downloaders.LinkGeneratorWorker(idsqueue, linksqueue, config['timeout_linkgenerator'])
        scrapper.daemon = True
        scrapper.start()
    for x in range(config['downloader_workers']):
        scrapper = Downloaders.LinkDownloaderWorker(linksqueue)
        scrapper.daemon = True
        scrapper.start()
    # app.run(host='0.0.0.0', debug=True, threaded=True)
    socket.run(app, host='0.0.0.0', debug=True)
