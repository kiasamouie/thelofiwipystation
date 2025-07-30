import getopt
import sys

from source import Source
from mix import Mix

# Default Values
title = ""
loop = r"D:\Premiere pro\20250403_210454.mp4"
url = "https://soundcloud.com/samui-music/sets/j-cole-kendrick-lamar-lo-fi-mashup"

try:
    arguments, values = getopt.getopt(sys.argv[1:], "t:u:l:m:", ["TITLE", "URL", "LOOP", "MIX"])
    for arg, val in arguments:
        if arg in ("-t", "--TITLE"):
            title = val
        if arg in ("-u", "--URL"):
            url = val
        if arg in ("-l", "--LOOP"):
            loop = val
        if arg in ("-m", "--MIX"):
            print(("MIX (% s)") % (val))

    source = Source(url, title)
    tracks_info = source.download()
    lofiwifi = Mix(
        tracks_info,
        loop=loop,
        # codec="h264_nvenc",
        # captions=True,
        # audio_only=True,
        # audio_type='wav',
        # n_times=6,
        # extra_seconds=2,
        # keep_tracks=True,
        # fade_in=2,
        # fade_out=2,
    )
    lofiwifi.Create_Mix()

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
