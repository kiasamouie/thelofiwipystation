import os
import json
import subprocess
import requests
import pyperclip

class Source:
    def __init__(self, url, title=None, save_directory=None, short_url=False):
        if isinstance(url, str):
            self.url = [url]
            default_title = url.rsplit("/", 1)[-1].title()
        else:
            self.url = url
            default_title = url[0].rsplit("/", 1)[-1].title() if url else "Unknown"
        self.title = title if title else default_title
        self.tracks_directory = os.path.join(save_directory or os.getcwd(), self.title, "tracks")
        os.makedirs(self.tracks_directory, exist_ok=True)
        self.short_url = short_url
        self.track_list_data = []

    def get_info(self, single_url):
        cmd = ['yt-dlp', '--dump-single-json', single_url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def download(self):
        urls_to_download = []
        for u in self.url:
            info = self.get_info(u)
            self._process_info(info)
            urls_to_download.append(u)
        self._download_tracks(urls_to_download)

    def _process_info(self, info):
        if 'entries' in info:
            for e in info['entries']:
                self.track_list_data.append({
                    "id": e.get('id'),
                    "title": f"{e.get('uploader')} - {e.get('title')}",
                    "url": self._url(e.get('webpage_url', ''))
                })
        else:
            self.track_list_data.append({
                "id": info.get('id'),
                "title": info.get('title'),
                "url": self._url(info.get('webpage_url', ''))
            })

    def _download_tracks(self, urls):
        if not urls:
            return
        cmd = [
            'yt-dlp',
            '--format', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '320K',
            '--output', os.path.join(self.tracks_directory, '%(id)s')
        ] + urls
        subprocess.run(cmd, check=True)

    def _url(self, url):
        if not self.short_url:
            return url
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": "https://on.soundcloud.com",
                "link": url
            },
            "suffix": {"option": "SHORT"}
        }
        r = requests.post(
            'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyCyJd9YWHCkMgshFd2nDL-Ig_qjnuUSH20',
            json=payload
        )
        return r.json().get('shortLink', url) if r.status_code == 200 else url