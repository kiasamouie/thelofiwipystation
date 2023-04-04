import math
import os
import shutil as sh
from datetime import timedelta

import eyed3
from moviepy.editor import *


class Mix:

    def __init__(
        self,
        track_list_data,
        tracks_directory,
        loop=None,
        audio_only=False,
        audio_type='mp3',
        n_times=1,
        extra_seconds=None,
        keep_tracks=False,
        fade_in=None,
        fade_out=None,
    ):
        self.track_list_data = track_list_data
        self.tracks_directory = tracks_directory
        self.__loop = loop
        self.__audio_only = audio_only

        self.__n_times = n_times
        self.__extra_seconds = extra_seconds
        self.__keep_tracks = keep_tracks
        self.__fade_in = fade_in
        self.__fade_out = fade_out

        self.__tracks = os.listdir(tracks_directory)
        self.__save_directory = tracks_directory.rsplit("\\", 1)[0]

        self.__audioFile = os.path.join(self.__save_directory, f"audio.{audio_type}")
        self.__videoFile = os.path.join(self.__save_directory, "video.mp4")

    def Create_Mix(self):
        audio = self.Clean_Audio_Info()
        if self.__audio_only:
            audio.write_audiofile(self.__audioFile)
        else:
            loop = self.Loop(audio)
            mix = [loop] * round(audio.duration / loop.duration)
            video = concatenate_videoclips(mix, method="compose")
            video.audio = audio

            if self.__fade_in:
                video = video.fadein(self.__fade_in)
            if self.__fade_out:
                video = video.fadeout(self.__fade_out)

            video.write_videofile(
                self.__videoFile,
                temp_audiofile=self.__audioFile,
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
        infoFile = open(os.path.join(self.__save_directory,"info.txt"), 'w', encoding="utf-8")
        for n in range(0, self.__n_times):
            last = n + 1 == self.__n_times
            for i, filename in enumerate(self.__tracks):
                mp3 = eyed3.load(os.path.join(self.tracks_directory, filename))
                secs = timedelta(seconds=int(mp3.info.time_secs))
                if i == 0 and n == 0:
                    timestamp = "0:00:00"
                    next = secs
                    if self.__extra_seconds:
                        next += timedelta(seconds=self.__extra_seconds)
                else:
                    timestamp = str(next)
                    next += secs
                if next.seconds - secs.seconds < 3600 and not over_hour:
                    timestamp = timestamp.split(':', 1)[1]

                count += 1
                backslash = "\n" if not last or filename != self.__tracks[-1] else ""
                track_name = self.track_list_data[i]['title']
                if n > 0:
                    track_name = track_name.split(" - ", 1)[0]

                infoFile.write(
                    f'{timestamp} - {str(count).zfill(2)} | {track_name}{backslash}')
            if self.__n_times > 1 and not last:
                infoFile.write(f"LOOP\n")

        infoFile.write("\n\n")
        track_list_urls = [obj['url'] for obj in self.track_list_data]
        for i, url in enumerate(track_list_urls):
            backslash = "\n" if url != track_list_urls[-1] else ""
            infoFile.write(f'{str(i+1).zfill(2)} - {url}{backslash}')
        infoFile.close()

    def Clean_Tracks(self):
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
        return concatenate_audioclips([AudioFileClip(os.path.join(self.tracks_directory, track)) for track in self.__tracks])

    def Loop(self, audio):
        if self.__loop.endswith(('png','jpg','jpeg')):
            return ImageClip(self.__loop).set_duration(audio.duration)
        elif self.__loop.endswith(('gif','mp4')):
            return VideoFileClip(self.__loop)