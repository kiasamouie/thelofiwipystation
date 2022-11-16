import sys
import os
import shutil as sh
import eyed3
import youtube_dl
import pyperclip
import json


class Source:

    __ydl = None

    track_list_data = []
    tracks_directory = None

    def __init__(self, title=None):
        self.title = title
        self.Init_YDL()

    def Download(self, url):
        if isinstance(url, str):
            # playlist url
            playlist = self.Get_Info(url)
            # self.title = playlist['title']
            for entry in playlist['entries']:
                track = self.Get_Info(entry['url'])
                self.track_list_data.append({
                    "id": entry['id'],
                    "title": f"{track['uploader']} - {track['title']}",
                    "url": track['webpage_url']
                })
            url = [url]
        else:
            # list of urls
            for u in url:
                obj = self.Get_Info(u)
                self.track_list_data.append({
                    "id": obj['id'],
                    "title": obj['title'],
                    "url": u
                })
        if not os.path.isdir(self.tracks_directory):
            self.__ydl.download(url)

    def Init_YDL(self):
        self.tracks_directory = os.path.join(os.getcwd(), self.title, "tracks")
        self.__ydl = youtube_dl.YoutubeDL(
            {
                'outtmpl': os.path.join(self.tracks_directory, "%(id)s.%(ext)s"),
                'format': 'bestaudio/best',
                'keepvideo': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }
        )

    def Get_Info(self, url):
        return self.__ydl.extract_info(url=url, download=False, process=False)
