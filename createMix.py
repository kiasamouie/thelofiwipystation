import getopt
import sys

from lofiwifi.source import Source
from lofiwifi.mix import Mix

# Default Values
title = "christmas lofi"
url = "https://soundcloud.com/thelofiwifistation/sets/christmas-lofi"
loop = "loop.gif"

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

    source = Source(title)
    source.Download(url)
    lofiwifi = Mix(
        source.track_list_data,
        source.tracks_directory,
        loop=loop,
        # n_times=6,
        # extra_seconds=7,
        # keep_tracks=True,
        fadein=2,
        fadeout=2,
    )
    lofiwifi.Create_Mix()

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
