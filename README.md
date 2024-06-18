# The Lofi WiFi PyStation

The Lofi WiFi PyStation is a Python package designed to download tracks from YouTube and create mix videos with various customizations. It leverages `youtube_dl` for downloading and `moviepy` for video creation, enabling users to generate personalized lofi music mixes.

## Features

- Download tracks or playlists from Souncloud.
- Create custom mix videos with options for looping, fading, and captions.
- Supports both audio-only and video output.
- Automatic cleanup of downloaded tracks after mix creation.

## Installation

To install the package, use the following command:

```sh
pip install git+https://github.com/kiasamouie/thelofiwipystation.git
```
## Usage
### Downloading Tracks
To download tracks from a YouTube playlist or a list of URLs:

```sh
from lofiwifi.source import Source

url = 'your_playlist_or_video_url_here'
source = Source(url, title='Your Mix Title', short_url=True)
source.Download()
```

### Creating a Mix
To create a mix from the downloaded tracks:

```sh
from lofiwifi.mix import Mix

track_list_data = source.track_list_data
tracks_directory = source.tracks_directory

mix = Mix(
    track_list_data=track_list_data,
    tracks_directory=tracks_directory,
    loop='path_to_your_loop_image_or_video',
    audio_only=False,
    n_times=1,
    keep_tracks=False,
    fade_in=5,
    fade_out=5,
    show_captions=True,
)

mix.Create_Mix()
```

Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

Acknowledgments
youtube-dl
moviepy
eyed3

This `README.md` file provides an overview of the project, installation instructions, usage examples, and additional information about licensing and contributions. Feel free to adjust the content based on your specific needs and preferences.
