import requests
import json
import os
import sys
import youtube_dl


class Source:

    __ydl = None

    track_list_data = []
    tracks_directory = None
    __short_url = None

    def __init__(self, url, title=None, short_url=False):
        self.url = url
        self.title = title if title else url.rsplit("/", 1)[1].title()
        self.tracks_directory = os.path.join(os.getcwd(), self.title, "tracks")
        self.__short_url = short_url
        self.__ydl = youtube_dl.YoutubeDL({
            'outtmpl': os.path.join(self.tracks_directory, "%(id)s.%(ext)s"),
            'format': 'bestaudio/best',
            'keepvideo': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        })
    
    def Get_Info(self, url):
        return self.__ydl.extract_info(url=url, download=False, process=False)

    def Download(self):
        if isinstance(self.url, str):
            # playlist url
            playlist = self.Get_Info(self.url)
            # self.title = playlist['title']
            for entry in playlist['entries']:
                track = self.Get_Info(entry['url'])
                self.track_list_data.append({
                    "id": entry['id'],
                    "title": f"{track['uploader']} - {track['title']}",
                    "url": self.Short_Url(track['webpage_url'])
                })
            self.url = [self.url]
        else:
            # list of urls
            for u in self.url:
                track = self.Get_Info(u)
                self.track_list_data.append({
                    "id": track['id'],
                    "title": track['title'],
                    "url": self.Short_Url(u)
                })
        if not os.path.isdir(self.tracks_directory):
            self.__ydl.download(self.url)

    def Short_Url(self, url):
        if not self.__short_url:
            return url
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": "https://on.soundcloud.com",
                "link": url
            },
            "suffix": {
                "option": "SHORT"
            }
        }
        response = requests.post('https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyCyJd9YWHCkMgshFd2nDL-Ig_qjnuUSH20', json=payload)
        if response.status_code == 200:
            return json.loads(response.text)['shortLink']
        else:
            return url