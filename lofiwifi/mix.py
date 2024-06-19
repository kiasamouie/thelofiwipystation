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
        keep_tracks=False,
        fade_in=None,
        fade_out=None,
        show_captions=None,
    ):
        self.track_list_data = track_list_data
        self.tracks_directory = tracks_directory
        self.__loop = loop
        self.__audio_only = audio_only

        self.__n_times = n_times
        self.__keep_tracks = keep_tracks
        self.__fade_in = fade_in
        self.__fade_out = fade_out

        self.__tracks = os.listdir(tracks_directory)
        self.__save_directory = tracks_directory.rsplit("\\", 1)[0]

        self.__audioFile = os.path.join(self.__save_directory, f"audio.{audio_type}")
        self.__videoFile = os.path.join(self.__save_directory, "video.mp4")
        
        self.__show_captions = show_captions
        self.__captions = []

    def Create_Mix(self):
        audio = self.Get_Info_Audio()
        if self.__audio_only:
            audio.write_audiofile(self.__audioFile)
        else:
            loop = self.Loop(audio)
            iterations = math.ceil(audio.duration / loop.duration)
            total_loop_seconds = loop.duration * iterations
            seconds_to_remove = total_loop_seconds - audio.duration
            
            while seconds_to_remove > loop.duration:
                iterations-=1
                seconds_to_remove -= loop.duration

            mix = [loop] * iterations
            if seconds_to_remove >=1:
                mix[-1] = loop.set_duration(loop.duration - seconds_to_remove)

            video = concatenate_videoclips(mix, method="compose")
            video.audio = audio

            if self.__fade_in:
                video = video.fadein(self.__fade_in)
            if self.__fade_out:
                video = video.fadeout(self.__fade_out)

            if self.__show_captions:
                video = CompositeVideoClip([video,
                    CompositeVideoClip(self.__captions)
                    .set_position(("left", "bottom"))
                    .margin(left=100, bottom=50, opacity=0)
                ])
            video.write_videofile(
                self.__videoFile,
                temp_audiofile=self.__audioFile,
                remove_temp=False,
                fps=24,
                threads=32,
                codec="h264_nvenc"
            )
        if not self.__keep_tracks:
            sh.rmtree(self.tracks_directory)

    def Get_Info_Audio(self):
        self.Clean_Tracks()
        audio = self.Create_Info_Audio()
        return audio
    
    def Clean_Tracks(self):
        track_list_ids = [track.id for track in self.track_list_data]
        for i, filename in enumerate(os.listdir(self.tracks_directory)):
            file = os.path.join(self.tracks_directory, filename)
            if not filename.endswith(".mp3"):
                os.remove(file)
                continue
            id = filename.replace(".mp3", '')
            name = f'{str(track_list_ids.index(id) + 1).zfill(2)}.{filename}'
            os.rename(file, os.path.join(self.tracks_directory, name))

    def Create_Info_Audio(self):
        merged_audio = []
        start = timedelta(seconds=0)
        count = 0
        next = 0
        total_duration = 0
        self.__tracks = os.listdir(self.tracks_directory)
        with open(os.path.join(self.__save_directory,"info.txt"), 'w', encoding="utf-8") as infoFile:
            for n in range(0, self.__n_times):
                last = n + 1 == self.__n_times
                for i, filename in enumerate(self.__tracks):
                    file = os.path.join(self.tracks_directory, filename)
                    merged_audio.append(AudioFileClip(file))
                    mp3 = eyed3.load(file)
                    secs = timedelta(seconds=int(mp3.info.time_secs))
                    total_duration += secs.seconds
                    if i == 0 and n == 0:
                        timestamp = "0:00:00"
                        next = secs
                    else:
                        start = next
                        timestamp = str(next)
                        next += secs
                    if next.seconds - secs.seconds < 3600 and not math.ceil(total_duration - secs.seconds * self.__n_times) > 3600:
                        timestamp = timestamp.split(':', 1)[1]

                    backslash = "\n" if not last or filename != self.__tracks[-1] else ""
                    track_name = self.track_list_data[i].title
                    
                    if n > 0:
                        track_name = track_name.split(" - ", 1)[0]

                    if self.__show_captions:
                        self.__captions.append(
                            TextClip(track_name, fontsize=24, color='white', font='Corbel Light')
                            .set_start(start.seconds)
                            .set_duration(mp3.info.time_secs)
                            .crossfadein(2)
                            .crossfadeout(2)
                        )
                    count += 1
                    infoFile.write(f'{timestamp} - {str(count).zfill(2)} | {track_name}{backslash}')

                if self.__n_times > 1 and not last:
                    infoFile.write(f"LOOP\n")

            infoFile.write("\n\n")
            track_list_urls = [track.url for track in self.track_list_data]
            for i, url in enumerate(track_list_urls):
                backslash = "\n" if url != track_list_urls[-1] else ""
                infoFile.write(f'{str(i+1).zfill(2)} - {url}{backslash}')
        return concatenate_audioclips(merged_audio)

    def Loop(self, audio):
        if self.__loop.endswith(('png','jpg','jpeg')):
            return ImageClip(self.__loop).set_duration(audio.duration)
        elif self.__loop.endswith(('gif','mp4')):
            return VideoFileClip(self.__loop)