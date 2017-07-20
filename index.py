# -*- coding: utf-8 -*-
import json
import utils.utils as UTILS
import utils.spotify as SPOT
import utils.pwsecurity as PWS
import utils.youtubemp3 as YTMP3
import sql.user as USER
import sql.playlist as PLAYLIST
from queue import Queue
from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socket = SocketIO(app)
DIRECTORY, SPOTIFY, linksqueue, idsqueue = None, None, None, None
config = json.load(open("config.json", "r"))

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/insert/user', methods=['POST'])
def insert_user():
    user = request.json
    user['password'] = PWS.hash(user['password'])
    USER.create_user(user=user)
    return json.dumps(True)

@app.route('/insert/playlist', methods=['POST'])
def insert_playlist():
    r = request.json
    songs = list(UTILS.scrap_youtube_playlist(r['url']))
    res = PLAYLIST.create_playlist(
        user_id=request.headers.get('User'),
        playlist=UTILS.youtube_playlist_data(r['url']),
        songs=songs)
    return json.dumps(res)

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
        socket.emit(str(user_id), dict(playlist_id=playlist_id, uuid=uuid, status='finished'), broadcast=True)

    playlist_id = request.json['playlistId']
    user_id = request.headers.get('User')

    # Mandar mensaje de descarga iniciada
    socket.emit(str(user_id), dict(playlist_id=playlist_id, status='started', c=0, t=1), broadcast=True)

    playlist = PLAYLIST.get_playlist_information(playlist_id, user_id)
    playlist_queue = Queue()
    playlist_path = DIRECTORY+playlist.get('uuid')
    UTILS.create_dir(playlist_path)
    length = len(playlist.get('songs'))
    for s, i in zip(playlist.get('songs'), range(length)):
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
    playlist_path = DIRECTORY+playlist.get('uuid')
    UTILS.create_dir(playlist_path)
    length = len(playlist.get('songs'))
    for s, i in zip(playlist.get('songs'), range(length)):
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
    SPOTIFY = SPOT.SpotifyManager(config['spotify_token'])
    SPOTIFY.get_sp_token()
    linksqueue, idsqueue = Queue(), Queue()
    for x in range(config['scrapper_workers']):
        scrapper = YTMP3.LinkGeneratorWorker(idsqueue, linksqueue, config['timeout_linkgenerator'])
        scrapper.daemon = True
        scrapper.start()
    for x in range(config['downloader_workers']):
        scrapper = YTMP3.LinkDownloaderWorker(linksqueue)
        scrapper.daemon = True
        scrapper.start()
    # app.run(host='0.0.0.0', debug=True, threaded=True)
    socket.run(app, host='0.0.0.0', debug=True)
