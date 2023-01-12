import os
import PySimpleGUI as sg

from lofiwifi.source import Source
from lofiwifi.mix import Mix

# pip install pysimplegui
# sg.theme('DarkBlack')
save_dir = os.path.expanduser('~\Documents')
soundcloud = [
    [sg.T('Title', size=(15, 1)), sg.Input('', key='title')],
    [sg.T('URL', size=(15, 1)), sg.Input('https://soundcloud.com/', key='url')],
    [sg.T('Loop Directory', size=(15, 1)), sg.Input('', key='loop'), sg.FileBrowse()],
    # [sg.T('Save Directory', size=(15, 1)),sg.Input(save_dir, key='save'), sg.FolderBrowse()],
]

app_layout = [
    [
        sg.TabGroup([[
            sg.Tab('Soundcloud', soundcloud),
        ]], enable_events=True, key="type")
    ],
    [
        sg.Column([[
            sg.Button('Submit'),
            sg.Button('Clear'),
            sg.Button('Close')
        ]], justification='right')
    ]
]
window = sg.Window('LofiWiPyStation', app_layout)


def clear_input(window, values):
    print(window)
    for key, element in window.key_dict.items():
        if isinstance(element, sg.Input):
            element.update(value='')


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Close':
        break

    if event == 'Clear':
        clear_input(window, values)
    if event != "Submit":
        continue
    if not values['title']:
        sg.Popup('Please select a Title')
        continue
    if not values['url']:
        sg.Popup('Please select a URL')
        continue
    if not values['loop']:
        sg.Popup('Please select a Loop')
        continue

    source = Source(values['title'])
    source.Download(values['url'])
    lofiwifi = Mix(
        source.track_list_data,
        source.tracks_directory,
        loop=values['loop'],
        # n_times=6,
        # extra_seconds=2,
        # keep_tracks=True,
        fadein=2,
        fadeout=2,
    )
    lofiwifi.Create_Mix()

window.close()