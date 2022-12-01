import PySimpleGUI as sg
from pathlib import Path
from PIL import Image
from io import BytesIO

_IMAGE_SEQUENCE = ["1-Reward_Visual.gif",
                   "2-tongue_sticking_out.gif",
                   "3-heart_eyes.gif",
                   "4-annoyance.gif",
                   "5-anger.gif",
                   "6-Infuriation.gif"]

def _image_to_data(im):
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


def haru_expression_gui():
    """Launch expressions UI."""
    images = [Image.open(Path(__file__).parent / "static"/ image_name) for image_name in _IMAGE_SEQUENCE]

    layout = [[sg.Text("Hello.")],
              [sg.Image(background_color='white', size = (392,468), key="haru", right_click_menu=["unused", ["Quit", "Next"]])]]

    image_index = 0
    frame_index = 0
    frames = None
    window = sg.Window("HAL 220").Layout(layout)
    while True:
        event, values = window.Read(timeout=5) # every 100ms, fire the event sg.TIMEOUT_KEY

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        elif event == sg.TIMEOUT_KEY:
            image = images[image_index]

            if frames is None:
                frames = images[image_index].n_frames

            image.seek(frame_index)
            data = _image_to_data(image)
                
            window["haru"].update(data)
            frame_index = (frame_index + 1) % frames

        elif event == "Next":
            frames = None
            frame_index = 0
            image_index = (image_index + 1) % len(images)

    window.close()
