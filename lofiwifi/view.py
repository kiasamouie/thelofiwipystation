import os
import PySimpleGUI as sg

from lofiwifi.source import Source
from lofiwifi.mix import Mix

# pip install pysimplegui
# sg.theme('DarkBlack')
save_dir = os.path.expanduser('~\Documents')
audio_types = ['mp3','wav']
loop_inputs = [
    sg.Input('', key='loop'), sg.FileBrowse()
]
fadeinout = [
    sg.Input('0', key='fade_in',size=(3,1)),
    sg.Input('0', key='fade_out',size=(3,1)),
]

mix = [
    [sg.T('Title', size=(15, 1)), sg.Input('', key='title')],
    [sg.T('URL', size=(15, 1)), sg.Input('https://soundcloud.com/', key='url')],
    [sg.T('Fade in/out', size=(15, 1))]
    + fadeinout,
    [sg.T('Loop Directory', size=(15, 1))] 
    + loop_inputs
    # [sg.T('Save Directory', size=(15, 1)),sg.Input(save_dir, key='save'), sg.FolderBrowse()],
]

app_layout = [
    [
        sg.TabGroup([[
            sg.Tab('Create Mix', mix),
        ]], enable_events=True, key="type")
    ],
    [
        sg.Column([[
            sg.Checkbox('Keep Tracks', default=False, enable_events=True, key='keep_tracks'),
            sg.Checkbox('Audio Only', default=False, enable_events=True, key='audio_only'),
            sg.Combo(values=audio_types, default_value=audio_types[0], size=(5, len(audio_types)), key='audio_type'),
            sg.Button('Submit'),
            sg.Button('Clear'),
            sg.Button('Close')
        ]], justification='right')
    ]
]
window = sg.Window('LofiWiPyStation', app_layout)

def clear_input(window, values):
    for key, element in window.key_dict.items():
        if isinstance(element, sg.Input):
            element.update(value='')

def toggle_loop(values):
    inputs = loop_inputs.copy() + fadeinout.copy()
    for input in inputs:
        input.update(disabled=values['audio_only'])
    inputs = None

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Close':
        break
    if event == 'audio_only':
        toggle_loop(values)
    # print(event)
    # print(values)
    if event == 'Clear':
        clear_input(window, values)
    if event != "Submit":
        continue
    if not values['url']:
        sg.Popup('Please select a URL')
        continue
    if not values['audio_only'] and not values['loop']:
        sg.Popup('Please select a Loop')
        continue
    try:
        values['fade_in'] = float(values['fade_in'])
        values['fade_out'] = float(values['fade_out'])
    except ValueError:
        sg.Popup('Fade In/Out values must be numbers')
        continue

    source = Source(values['url'], values['title'])
    source.Download()
    lofiwifi = Mix(
        source.track_list_data,
        source.tracks_directory,
        loop=values['loop'],
        audio_only=values['audio_only'],
        audio_type=values['audio_type'],
        keep_tracks=values['keep_tracks'],
        fade_in=values['fade_in'],
        fade_out=values['fade_out'],
    )
    lofiwifi.Create_Mix()

window.close()