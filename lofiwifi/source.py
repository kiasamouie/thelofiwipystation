import os
import json
import subprocess
import requests

class Source:
    def __init__(self, url, title=None, save_directory=None, short_url=False, audio_format='wav'):
        if isinstance(url, str):
            self.url = [url]
            default_title = url.rsplit("/", 1)[-1].title()
        else:
            self.url = url
            default_title = url[0].rsplit("/", 1)[-1].title() if url else "Unknown"
        self.title = title if title else default_title
        self.short_url = short_url
        self.tracks_info = {
            "audio_format": audio_format,
            "directory": os.path.join(save_directory or os.getcwd(), self.title, "tracks"),
            "url": url,
            "data": []
        }
        os.makedirs(self.tracks_info['directory'], exist_ok=True)

    def get_info(self, single_url):
        cmd = ['yt-dlp', '--dump-single-json', single_url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def download(self):
        urls = []
        for u in self.url:
            info = self.get_info(u)
            self._process_info(info)
            urls.append(u)
        subprocess.run([
            'yt-dlp',
            '--format', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', self.tracks_info['audio_format'],
            '--audio-quality', '320K',
            '--output', os.path.join(self.tracks_info['directory'], '%(id)s')
        ] + urls, check=True)
        return self.tracks_info

    def _process_info(self, info):
        if 'entries' in info:
            for e in info['entries']:
                self.tracks_info['data'].append({
                    "id": e.get('id'),
                    "title": f"{e.get('uploader')} - {e.get('title')}",
                    "url": self._url(e.get('webpage_url', '')),
                    "duration": e.get('duration')
                })
        else:
            self.tracks_info['data'].append({
                "id": info.get('id'),
                "title": info.get('title'),
                "url": self._url(info.get('webpage_url', '')),
                "duration": info.get('duration')
            })

    def _url(self, url):
        if not self.short_url:
            return url
        r = requests.post(
            'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyCyJd9YWHCkMgshFd2nDL-Ig_qjnuUSH20',
            json={
                "dynamicLinkInfo": {
                    "domainUriPrefix": "https://on.soundcloud.com",
                    "link": url
                },
                "suffix": {"option": "SHORT"}
            }
        )
        return r.json().get('shortLink', url) if r.status_code == 200 else url