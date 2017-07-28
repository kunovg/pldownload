import re
import os
import uuid
import glob
import shutil
import zipfile
import datetime

def remove_special_characters(s):
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        if ch in s:
            s = s.replace(ch, "")
    return s

def get_playlist_source(url):
    # Hacer bien esta funcion
    return 'Spotify' if 'spot' in url else 'YouTube'

def get_sp_playlist_data(url):
    user = re.search(r'(?<=user\/|user:)(.*)(?=\/playlist|:playlist)', url).group(0)
    idplaylist = re.search(r'(?<=playlist\/|playlist:)(.*)', url).group(0)
    return {'user': user, 'idplaylist': idplaylist}

def gen_uuid():
    return str(uuid.uuid4())

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
