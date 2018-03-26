# -*- coding: utf-8 -*-
import eventlet
import json
import logging
from queue import Queue
from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_claims

import utils.utils as utils
import utils.pwsecurity as pwsecurity
import sql.user as sql_user
import sql.playlist as sql_playlist
import platforms.spotify as spotify
import platforms.soundcloud as soundcloud
from platforms.youtube import Youtube
from workers.linkdownloader import LinkDownloader
from workers.linkgenerator import LinkGenerator

config = json.load(open("config.json", "r"))
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

eventlet.monkey_patch()  # Resuelve el emit dentro de threads
app = Flask(__name__)
app.secret_key = config['app_secret_key']
CORS(app)
jwt = JWTManager(app)
socket = SocketIO(app)
Spotify = None
idsqueue = None
SoundCloud = None
linksqueue = None

DIRECTORY = None

# Using the user_claims_loader, we can specify a method that will be
# called when creating access tokens, and add these claims to the said
# token. This method is passed the identity of who the token is being
# created for, and must return data that is json serializable
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    info = sql_user.get_basic_info(identity)
    return {
        'name': info['name'],
        'id': identity
    }

@app.route("/")
def index():
    logger.debug("Index")
    return render_template('index.html')

@app.route("/valid_token")
@jwt_required
def valid_token():
    logger.debug("Valid Token")
    return ('', 200)

@app.route('/login', methods=['POST'])
def login():
    logger.debug("Login")
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    _id = sql_user.valid_password(
        password=request.json['password'],
        name=request.json['name'])
    if not _id:
        return jsonify({"msg": "Wrong username or password"}), 400
    # Identity can be any data that is json serializable
    ret = {'access_token': create_access_token(identity=_id)}
    return jsonify(ret), 200

@app.route('/user/create', methods=['POST'])
def insert_user():
    logger.debug("Insert User")
    user = request.json
    user['password'] = pwsecurity.hash(user['password'])
    sql_user.create_user(user=user)
    return json.dumps(True)

@app.route('/playlist/create', methods=['POST'])
@jwt_required
def insert_playlist():
    logger.debug("Insert Playlist")
    url = request.json.get('url')
    source = utils.get_playlist_source(url)
    if source == 'YouTube':
        songs = list(Youtube.scrap_playlist(url))
        name = Youtube.get_yt_playlist_title(url)
    elif source == 'Spotify':
        user, idplaylist = Spotify.get_user_and_id(url)
        songs = Spotify.scrap_playlist(user, idplaylist)
        name = Spotify.get_sp_tracklist_name(url)
    elif source == 'SoundCloud':
        songs = SoundCloud.scrap_playlist(url)
        name = SoundCloud.get_playlist_name(url)
    res = sql_playlist.create_playlist(
        user_id=get_jwt_claims()['id'],
        playlist=dict(source=source, url=url, name=name),
        songs=songs)
    return json.dumps(res)

@app.route('/playlist/update', methods=['POST'])
@jwt_required
def update_playlist():
    logger.debug("Update Playlist")
    r = request.json
    source, url = r.get('source'), r.get('url')
    if source == 'YouTube':
        songs = list(Youtube.scrap_playlist(url))
    elif source == 'Spotify':
        user, idplaylist = Spotify.get_user_and_id(url)
        songs = Spotify.scrap_playlist(user, idplaylist)
    elif source == 'SoundCloud':
        songs = SoundCloud.scrap_playlist(url)
    assert songs
    res = sql_playlist.update_playlist(
        playlist_id=r.get('id'),
        user_id=get_jwt_claims()['id'],
        songs=songs)
    return json.dumps(res)

@app.route('/playlist/unlink', methods=['POST'])
@jwt_required
def unlink_playlist():
    logger.debug("Unlink Playlist")
    sql_playlist.unlink_playlist(
        user_id=get_jwt_claims()['id'],
        playlist_id=request.json['id'])
    return '', 200

@app.route('/validate', methods=['POST'])
def validate():
    logger.debug("Validate Playlist")
    attr, name = list(request.json.items())[0]
    return json.dumps(sql_user.valid(attr, name))

@app.route('/playlists', methods=['GET'])
@jwt_required
def get_playlists():
    logger.debug("Get Playlists")
    return json.dumps(sql_user.get_playlists(get_jwt_claims()['id']))

@app.route('/fulldownload', methods=['POST'])
@jwt_required
def fulldownload():
    logger.debug("Full download")
    def finished_download_callback(user_id, playlist_id, uuid, songs_id, tipo):
        sql_playlist.update_last_date_type(playlist_id, user_id, tipo)
        sql_playlist.add_downloaded(user_id, playlist_id, songs_id=songs_id)
        socket.emit(str(user_id), dict(playlist_id=playlist_id, uuid=uuid,
                                       status='finished'), broadcast=True)

    playlist_id = request.json['playlistId']
    user_id = get_jwt_claims()['id']

    # Mandar mensaje de descarga iniciada
    socket.emit(str(user_id), dict(playlist_id=playlist_id, status='started',
                                   c=0, t=1), broadcast=True)

    playlist = sql_playlist.get_playlist_information(playlist_id, user_id)
    playlist_queue = Queue()
    playlist_path = DIRECTORY + playlist['uuid']
    utils.create_dir(playlist_path)
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
@jwt_required
def partialdownload():
    logger.debug("Partial download")
    def finished_download_callback(user_id, playlist_id, uuid, songs_id, tipo):
        sql_playlist.update_last_date_type(playlist_id, user_id, tipo)
        sql_playlist.add_downloaded(user_id, playlist_id, songs_id=songs_id)
        socket.emit(str(user_id), dict(playlist_id=playlist_id, uuid=uuid,
                                       status='finished'), broadcast=True)

    playlist_id = request.json['playlistId']
    user_id = get_jwt_claims()['id']

    # Mandar mensaje de descarga iniciada
    socket.emit(str(user_id), dict(playlist_id=playlist_id, status='started',
                                   c=0, t=1), broadcast=True)

    playlist = sql_playlist.get_playlist_information(playlist_id, user_id)
    playlist_queue = Queue()
    playlist_path = DIRECTORY + playlist['uuid']
    utils.create_dir(playlist_path)
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
    logger.debug("Get file")
    return send_file(
        as_attachment=True,
        mimetype="application/zip",
        filename_or_fp="{}{}.zip".format(DIRECTORY, request.args.get('uuid')))

if __name__ == "__main__":
    DIRECTORY = config['file_directory']
    Spotify = spotify.Spotify(config['spotify_token'])
    Spotify.get_sp_token()
    SoundCloud = soundcloud.SoundCloud(config['soundcloud_client_id'])
    linksqueue, idsqueue = Queue(), Queue()
    for x in range(config['scrapper_workers']):
        scrapper = LinkGenerator(idsqueue, linksqueue,
            config['timeout_linkgenerator'], config['soundcloud_client_id'])
        scrapper.daemon = True
        scrapper.start()
    for x in range(config['downloader_workers']):
        scrapper = LinkDownloader(linksqueue)
        scrapper.daemon = True
        scrapper.start()
    # app.run(host='0.0.0.0', debug=True, threaded=True)
    socket.run(app, host='0.0.0.0', debug=True)
