import getopt
import sys

from lofiwifi.source import Source
from lofiwifi.mix import Mix

# Default Values
title = "Sonic"
loop = "sonic.jpg"
url = [
    "https://www.youtube.com/watch?v=hPIM9KfMW8s",
    "https://soundcloud.com/andrewoneaware/the-streets-of-rage-crime-city-lofi-remix",
    "https://soundcloud.com/melodieszone/wilderness-lofigolden-axe",
    "https://www.youtube.com/watch?v=gdsMklAtDyw",
    "https://www.youtube.com/watch?v=RIV8X3U_m3Q",
    "https://soundcloud.com/amphee/make-eggs-throw-eggs",
    "https://soundcloud.com/user-677008859/green-hills",
    "https://www.youtube.com/watch?v=ScximJGRI7s",
    "https://www.youtube.com/watch?v=qfhe1HtBWTc",
    "https://www.youtube.com/watch?v=b0EZi14yQcU"
]

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
    source.Download()
    lofiwifi = Mix(
        source.track_list_data,
        source.tracks_directory,
        loop=loop,
        # audio_only=True,
        # audio_type='wav',
        # n_times=6,
        # extra_seconds=2,
        # keep_tracks=True,
        fadein=2,
        fadeout=2,
    )
    lofiwifi.Create_Mix()

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
