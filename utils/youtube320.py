import requests
import re

def descarga320(id_video):
    try:
        youtubeid = "https://www.youtube.com/watch?v=" + id_video
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept-Encoding': 'gzip, deflate, br'}
        data = {'videoURL': youtubeid, 'quality': '320', 'submit': 'Convert+To+MP3'}
        r = requests.post('https://vubey.yt/', headers=headers, data=data)
        urlredir = re.compile('.download=................................').search(str(r.content)).group()
        descarga = 'https://vubey.yt/'+str(urlredir)
        r = requests.get(descarga, headers=headers)
        buscar = str(re.compile('Please wait, your video is being converted to MP3').search(str(r.content)))
        while buscar == str(re.compile('Please wait, your video is being converted to MP3').search(str(r.content))):
            r = requests.get(descarga, headers=headers)

        urlfinal = str(re.compile('https:..dl1.tubeapi.com.+?(?=.mp3)').search(str(r.content)).group())+'.mp3'
        # print(urlfinal)
        return urlfinal
    except:
        return False

descarga320("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
# mix de 1hr Descarga320("https://www.youtube.com/watch?v=xaBKstKrDAg&index=137&list=FLoBm9kzMntq20PdFBLoDvKg")
