import os
import shutil as sh
import eyed3
import math
from datetime import timedelta
from moviepy.editor import *


class Mix:

    def __init__(
        self,
        track_list_data,
        tracks_directory,
        loop=None,
        n_times=1,
        extra_seconds=None,
        keep_tracks=False,
        fadein=None,
        fadeout=None,
    ):
        self.track_list_data = track_list_data
        self.tracks_directory = tracks_directory
        self.__loop = loop

        self.__n_times = n_times
        self.__extra_seconds = extra_seconds
        self.__keep_tracks = keep_tracks
        self.__fadein = fadein
        self.__fadeout = fadeout

        self.__tracks = os.listdir(tracks_directory)
        self.__save_directory = tracks_directory.rsplit("\\", 1)[0]

    def Create_Mix_Audio(self):
        audio = self.Clean_Audio_Info()
        audio.write_audiofile(os.path.join(self.__save_directory, "audio.mp3"))
        if not self.__keep_tracks:
            sh.rmtree(self.tracks_directory)

    def Create_Mix(self):
        audio = self.Clean_Audio_Info()
        loop = VideoFileClip(self.__loop)
        mix = [loop] * round(audio.duration / loop.duration)
        video = concatenate_videoclips(mix, method="compose")
        video.audio = audio

        if self.__fadein:
            video = video.fadein(self.__fadein)
        if self.__fadeout:
            video = video.fadeout(self.__fadeout)

        video.write_videofile(
            os.path.join(self.__save_directory, "video.mp4"),
            temp_audiofile=os.path.join(self.__save_directory, "audio.mp3"),
            remove_temp=False,
            fps=24,
            threads=32,
            codec="libx264"
        )
        if not self.__keep_tracks:
            sh.rmtree(self.tracks_directory)

    def Clean_Audio_Info(self):
        self.Clean_Tracks()
        audio = self.Audio()
        self.Create_Info(audio.duration)
        return audio

    def Create_Info(self, duration):
        count = 0
        next = 0
        self.__tracks = os.listdir(self.tracks_directory)
        over_hour = math.ceil(duration * self.__n_times) > 3600
        fileInfo = open(os.path.join(self.__save_directory,"info.txt"),'w',encoding="utf-8")
        for n in range(0, self.__n_times):
            last = n + 1 == self.__n_times
            if self.__extra_seconds and n > 0:
                next += timedelta(seconds=self.__extra_seconds)
            for i, filename in enumerate(self.__tracks):
                mp3 = eyed3.load(os.path.join(self.tracks_directory, filename))
                secs = timedelta(seconds=int(mp3.info.time_secs))
                if i == 0 and n == 0:
                    timestamp = "0:00:00"
                    next = secs
                else:
                    timestamp = str(next)
                    next += secs
                if next.seconds - secs.seconds < 3600 and not over_hour:
                    timestamp = timestamp.split(':', 1)[1]

                backslash = "\n" if not last or filename != self.__tracks[-1] else ""
                track_name = self.track_list_data[i]['title']
                count += 1

                fileInfo.write(f'{timestamp} - {str(count).zfill(2)} | {track_name}{backslash}')
            if self.__n_times > 1 and not last:
                fileInfo.write(f"LOOP\n")

        fileInfo.write("\n\n")
        track_list_urls = [obj['url'] for obj in self.track_list_data]
        for i, url in enumerate(track_list_urls):
            backslash = "\n" if url != track_list_urls[-1] else ""
            fileInfo.write(f'{str(i+1).zfill(2)} - {url}{backslash}')
        fileInfo.close()

    def Clean_Tracks(self):
        if os.path.isdir(self.tracks_directory):
            return
        track_list_ids = [obj['id'] for obj in self.track_list_data]
        for i, filename in enumerate(os.listdir(self.tracks_directory)):
            name = ''
            file = os.path.join(self.tracks_directory, filename)
            if not filename.endswith(".mp3"):
                os.remove(file)
                continue
            id = filename.replace(".mp3", '')
            name = f'{str(track_list_ids.index(id) + 1).zfill(2)}.{filename}'
            os.rename(file, os.path.join(self.tracks_directory, name))

    def Audio(self):
        self.__tracks = os.listdir(self.tracks_directory)
        return concatenate_audioclips(
            [AudioFileClip(os.path.join(self.tracks_directory, track)) for track in self.__tracks]
        )
