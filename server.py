# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import utils.sql as SQL
import utils.utils as U
import utils.pwsecurity as PWS
import utils.youtubemp3 as YTMP3
import utils.spotify as SPOT
from queue import Queue
from flask import Flask, render_template, request, session, redirect, url_for, send_file
# from socketIO_client import SocketIO, LoggingNamespace

app = Flask(__name__)
app.secret_key = None
CONFIG = None
DB = None
log = None
DIRECTORY = None
SPOTIFY = None
linksqueue = None
idsqueue = None

@app.route("/")
def index():
    playlists = []
    if session.get('logged_in'):
        u_id = DB.get_user_id(username=session['username'])
        for pl_id, uuid in DB.get_user_playlists(iduser=u_id):
            pl = DB.get_playlist_info(idplaylist=pl_id)
            total_songs = DB.get_playlist_total_songs(uuid=uuid)
            playlists.append({
                'title': pl[0],
                'source': pl[1],
                'total': total_songs,
                'total_news': total_songs - len(DB.get_user_downloaded(iduser=u_id, idplaylist=pl_id)),
                'url1': url_for('download', uuid=uuid, fop='f', title=pl[0]),
                'url2': url_for('download', uuid=uuid, fop='p', title=pl[0]),
                'uuid': uuid
            })
    return render_template(
        'index.html',
        session=session if session.get('logged_in') else None,
        playlists=playlists,
        socket=CONFIG['socket_server'])

@app.route('/insertpl', methods=['POST'])
def insertpl():
    user = session['username']
    playlist = request.form['plurl']
    u_id = session['user_id']
    log.write("{} user: {}\tplaylist {}\n".format(datetime.datetime.now(), user, playlist))

    if 'youtu' in playlist:
        source = 'youtube'
        title = U.get_yt_playlist_title(playlist)
    elif 'spotify' in playlist:
        source = 'spotify'
        playlist_data = U.get_sp_playlist_data(playlist)
        title = SPOTIFY.get_sp_tracklist_name(user=playlist_data['user'], listaid=playlist_data['idplaylist'])
    else:
        return ('', 400)

    pl_id = DB.insert_playlist(title, playlist, source)
    DB.add_playlist_to_user(iduser=u_id, idplaylist=pl_id)

    uuid = DB.get_uuid(iduser=u_id, idplaylist=pl_id)
    pl_directory = DIRECTORY + uuid
    U.crate_dir(pl_directory)

    if source == 'youtube':
        for song_id in DB.scrap_youtube_playlist(url=playlist, uuid=uuid):
            pass  # song_id
    else:
        for song_id in DB.scrap_spotify_playlist(spotify_inst=SPOTIFY, spotify_user=playlist_data['user'], listaid=playlist_data['idplaylist'], uuid=uuid):
            pass  # print(song_id)
    return ('', 200)

@app.route('/delete', methods=['POST'])
def delete_playlist():
    uuid = request.form['uuid']
    DB.delete_playlist(uuid=uuid)
    return('', 200)

@app.route('/update', methods=['POST'])
def update():
    uuid = request.form['uuid']
    log.write("{}\t Update {}\n".format(datetime.datetime.now(), uuid))
    pl_id = DB.get_playlists_id(uuid=uuid)[0]
    pl_info = DB.get_playlist_url_source_user(idplaylist=pl_id)
    old_pl_ids = set(DB.get_songs_id_from_uuid(uuid=uuid))
    new_pl_ids = set()

    if pl_info[1] == 'youtube':
        for song_id in DB.scrap_youtube_playlist(url=pl_info[0], uuid=uuid, need_id=True):
            new_pl_ids.add(song_id)
    else:
        playlist_data = U.get_sp_playlist_data(pl_info[0])
        for song_id in DB.scrap_spotify_playlist(spotify_inst=SPOTIFY, spotify_user=playlist_data['user'], listaid=playlist_data['idplaylist'], uuid=uuid):
            new_pl_ids.add(song_id)

    deleted_songs = old_pl_ids - new_pl_ids
    for s in deleted_songs:
        DB.delete_song(idsong=s)
    return ('', 200)

@app.route('/dl/<uuid>', methods=['GET', 'POST'])
def download(uuid):
    t1 = time.time()
    log.write("{}\t Download {}\n".format(datetime.datetime.now(), uuid))
    fop = request.args.get('fop')
    title = U.prepare_string_for_file(request.args.get('title'))
    pl_id = DB.get_playlists_id(uuid=uuid)[0]
    user_id = DB.get_user_id(uuid=uuid)
    pl_directory = DIRECTORY + uuid
    U.crate_dir(pl_directory)
    this_playlist_queue = Queue()
    this_playlist_queue.put(True)
    if fop == 'p':
        log.write("{}\t partial {}\n".format(datetime.datetime.now(), pl_id))
        set1 = set(DB.get_songs_id_from_uuid(uuid=uuid))
        set2 = set(DB.get_user_downloaded(iduser=user_id, idplaylist=pl_id))
        set3 = set1 - set2
    elif fop == 'f':
        log.write("{}\t full {}\n".format(datetime.datetime.now(), pl_id))
        set3 = set(DB.get_songs_id_from_uuid(uuid=uuid))
    else:
        return ('', 400)

    total_songs = len(set3)

    with open("{}.m3u".format(os.path.join(pl_directory, title)), "w+") as playlist_file:
        for song, i in zip(set3, range(total_songs)):
            try:
                s_info = DB.get_song_info(songid=song)
                idsqueue.put((pl_directory, U.prepare_string_for_file(s_info[1]), s_info[0], i+1, total_songs, this_playlist_queue))
                DB.add_user_downloaded(iduser=user_id, idsong=song, idplaylist=pl_id)
                playlist_file.write("{}.mp3\n".format(U.prepare_string_for_file(s_info[1])))
            except:
                print("ERROR ADDING TO QUEUE")

    this_playlist_queue.join()
    U.create_zip(folder_uuid=pl_directory, file_name=DIRECTORY + title)
    U.delete_files(pl_directory)
    print("Time elapsed: {}".format(time.time()-t1))
    return send_file(filename_or_fp="{}.zip".format(DIRECTORY + title), mimetype="application/zip", as_attachment=True)

@app.route('/freedownload', methods=['POST'])
def freedownload():
    t1 = time.time()
    # temp_id = request.form['temp_id']
    playlist_url = request.form['playlist_url']
    log.write("{} user: {} playlist{}".format(datetime.datetime.now(), None, playlist_url))
    uuid = U.gen_uuid()
    pl_directory = DIRECTORY + uuid
    U.crate_dir(pl_directory)
    this_playlist_queue = Queue()
    this_playlist_queue.put(True)
    if 'youtu' in playlist_url:
        title = U.get_yt_playlist_title(playlist_url)
        total_songs = U.count_youtube_playlist(playlist_url)
        with open("{}.m3u".format(os.path.join(pl_directory, title)), "w+") as playlist_file:
            for (idyt, name), i in zip(U.scrap_youtube_playlist_anon(url=playlist_url), range(total_songs)):
                try:
                    mp3name = U.prepare_string_for_file(name)
                    idsqueue.put((pl_directory, mp3name, idyt, i+1, total_songs, this_playlist_queue))
                    playlist_file.write("{}.mp3\n".format(mp3name))
                except:
                    print("ERROR ADDING TO QUEUE")

    elif 'spotify' in playlist_url:
        playlist_data = U.get_sp_playlist_data(playlist_url)
        spotify_user = playlist_data['user']
        listaid = playlist_data['idplaylist']
        title = SPOTIFY.get_sp_tracklist_name(user=spotify_user, listaid=listaid)
        total_songs = SPOTIFY.count_spotify_playlist(spotify_user=spotify_user, listaid=listaid)
        with open("{}.m3u".format(os.path.join(pl_directory, title)), "w+") as playlist_file:
            for (idyt, name), i in zip(SPOTIFY.scrap_spotify_playlist_anon(spotify_user=spotify_user, listaid=listaid), range(total_songs)):
                try:
                    mp3name = U.prepare_string_for_file(name)
                    idsqueue.put((pl_directory, mp3name, idyt, i+1, total_songs, this_playlist_queue))
                    playlist_file.write("{}.mp3\n".format(mp3name))
                except:
                    print("ERROR ADDING TO QUEUE")

    this_playlist_queue.join()
    log.write("{} Creando Comprimido {}\n".format(datetime.datetime.now(), 'ANON'))
    U.create_zip(folder_uuid=pl_directory, file_name=pl_directory)
    U.delete_files(pl_directory)
    print("Time elapsed: {}".format(time.time()-t1))
    return (uuid, 200)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        user = request.form['login_email']
        if PWS.check_password(plain_text_password=request.form['login_password'], hashed_password=DB.get_user_pw(username=user)):
            iduser = DB.get_user_id(username=user if "@" not in user else None, email=user if "@" in user else None)
            session['logged_in'] = True
            session['username'] = DB.get_username(iduser=iduser)
            session['user_id'] = iduser
            return ('', 200)
        return ('', 400)
    except:
        log.write("{}\tError desconocido en Login para usuario {}\n".format(datetime.datetime.now(), request.form.get('login_email')))
        return ('', 400)

@app.route('/report', methods=['POST'])
def report():
    try:
        DB.insert_error(
            description=request.form['description'],
            iduser=request.form['user_id'],
            playlist=request.form['playlist'],
            songname=request.form['songname'])
        return('', 200)
    except:
        return ('', 400)

@app.route('/changepw', methods=['POST'])
def changepw():
    if PWS.check_password(plain_text_password=request.form['oldpw'], hashed_password=DB.get_user_pw(iduser=request.form['user_id'])):
        DB.change_user_pw(iduser=request.form['user_id'], password=PWS.get_hashed_password(request.form['newpw'].encode('utf-8')).decode())
        log.write("{}\tUsuario {} cambio su contraseña\n".format(datetime.datetime.now(), request.form['user_id']))
        return ('', 200)
    return ('', 400)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/getzip/<uuid>', methods=['GET', 'POST'])
def get_zip(uuid):
    return send_file(filename_or_fp="{}.zip".format(DIRECTORY + uuid), mimetype="application/zip", as_attachment=True)

@app.route('/check_username', methods=['POST'])
def check_valid_username():
    if DB.get_user_id(username=request.form['username']):
        return ('', 400)
    return ('', 204)

@app.route('/check_email', methods=['POST'])
def check_valid_email():
    if DB.get_user_id(email=request.form['email']):
        return ('', 400)
    return ('', 204)

@app.route('/add', methods=['POST'])
def add_user():
    if DB.insert_user(username=request.form['username'], password=PWS.get_hashed_password(request.form['password'].encode('utf-8')).decode(), email=request.form['email']):
        log.write("{}\tUsuario nuevo añadido {}\n".format(datetime.datetime.now(), request.form['username']))
        session['logged_in'] = True
        session['username'] = request.form['username']
        return ('', 204)
    return ('', 400)

if __name__ == "__main__":
    log = open("log.txt", 'a+')
    CONFIG = json.load(open("config.json", "r"))
    connection = CONFIG['database_connection']
    app.secret_key = CONFIG['secret_key']
    DB = SQL.Connection(connection['driver'], connection['server'], connection['database'], connection['user'], connection['password'])
    DIRECTORY = CONFIG['file_directory']
    SPOTIFY = SPOT.SpotifyManager(CONFIG['spotify_token'])
    SPOTIFY.get_sp_token()
    linksqueue, idsqueue = Queue(), Queue()
    for x in range(CONFIG['scrapper_workers']):
        scrapper = YTMP3.LinkGeneratorWorker(idsqueue, linksqueue, CONFIG['timeout_linkgenerator'])
        scrapper.daemon = True
        scrapper.start()
    for x in range(CONFIG['downloader_workers']):
        scrapper = YTMP3.LinkDownloaderWorker(linksqueue)
        scrapper.daemon = True
        scrapper.start()
    print("TIMEOUT: {}\tDOWNLOADERS: {}".format(CONFIG['timeout_linkgenerator'], CONFIG['downloader_workers']))
    app.run(host='0.0.0.0', debug=False, threaded=True, port=5001)
