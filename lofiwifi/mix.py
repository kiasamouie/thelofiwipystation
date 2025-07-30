import math
import os
import shutil as sh
from datetime import timedelta

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.fx import FadeIn, FadeOut


class Mix:

    def __init__(
        self,
        tracks_info,
        loop=None,
        audio_only=False,
        n_times=1,
        keep_tracks=False,
        fade_in=None,
        fade_out=None,
        show_captions=None,
        codec="libx264",
    ):
        self.tracks_info = tracks_info
        self.__save_directory = os.path.dirname(self.tracks_info['directory'])

        self.__audioFile = os.path.join(self.__save_directory, f"audio.{self.tracks_info['audio_format']}")
        self.__videoFile = os.path.join(self.__save_directory, "video.mp4")
        self.__infoFile = os.path.join(self.__save_directory, "info.txt")
        
        self.__loop = loop
        self.__audio_only = audio_only

        self.__n_times = n_times
        self.__keep_tracks = keep_tracks
        self.__fade_in = fade_in
        self.__fade_out = fade_out
        
        self.__show_captions = show_captions
        self.__captions = []
        self.__codec = codec

    def Create_Mix(self):
        audio = self.Create_Info_Audio()
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
                mix[-1] = loop.with_duration(loop.duration - seconds_to_remove)

            video = concatenate_videoclips(mix, method="compose")
            video.audio = audio

            if self.__fade_in:
                video = FadeIn(video,self.__fade_in)
            if self.__fade_out:
                video = FadeOut(video, self.__fade_out)

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
                codec=self.__codec
            )
        if not self.__keep_tracks:
            sh.rmtree(self.tracks_info['directory'])
        return {
            'audio':self.__audioFile,
            'video':self.__videoFile,
            'info':self.__infoFile,
            'save_directory':self.__save_directory
        }

    def Create_Info_Audio(self):
        merged_audio = []
        start = timedelta(seconds=0)
        count = 0
        next = 0
        total_duration = 0
        tracks = [f"{track['id']}.{self.tracks_info['audio_format']}" for track in self.tracks_info['data']]
        with open(os.path.join(self.__infoFile), 'w', encoding="utf-8") as infoFile:
            for n in range(0, self.__n_times):
                last = n + 1 == self.__n_times
                for i, filename in enumerate(tracks):
                    merged_audio.append(AudioFileClip(os.path.join(self.tracks_info['directory'], filename)))
                    duration = int(self.tracks_info['data'][i]['duration'])
                    secs = timedelta(seconds=duration)
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

                    backslash = "\n" if not last or filename != tracks[-1] else ""
                    track_name = self.tracks_info['data'][i]['title']
                    
                    if n > 0:
                        track_name = track_name.split(" - ", 1)[0]

                    if self.__show_captions:
                        self.__captions.append(
                            TextClip(track_name, fontsize=24, color='white', font='Corbel Light')
                            .set_start(start.seconds)
                            .set_duration(duration)
                            .crossfadein(2)
                            .crossfadeout(2)
                        )
                    count += 1
                    infoFile.write(f'{timestamp} - {str(count).zfill(2)} | {track_name}{backslash}')

                if self.__n_times > 1 and not last:
                    infoFile.write(f"LOOP\n")

            infoFile.write("\n\n")
            track_list_urls = [track['url'] for track in self.tracks_info['data']]
            for i, url in enumerate(track_list_urls):
                backslash = "\n" if url != track_list_urls[-1] else ""
                infoFile.write(f'{str(i+1).zfill(2)} - {url}{backslash}')
            infoFile.write("\n\n")
            infoFile.write(self.tracks_info['url'])
        return concatenate_audioclips(merged_audio)

    def Loop(self, audio):
        if self.__loop.endswith(('png','jpg','jpeg')):
            return ImageClip(self.__loop).with_duration(audio.duration)
        elif self.__loop.endswith(('gif','mp4')):
            return VideoFileClip(self.__loop)