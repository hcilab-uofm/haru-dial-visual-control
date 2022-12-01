import PySimpleGUI as sg
from pathlib import Path
from PIL import Image
from io import BytesIO
from loguru import logger
from haru_dial_visual_control._phidget_manager import PhidgetDialSensorManager, setup_callbacks

_IMAGE_SEQUENCE = ["1-Reward_Visual.gif",
                   "2-tongue_sticking_out.gif",
                   "3-heart_eyes.gif",
                   "4-annoyance.gif",
                   "5-anger.gif",
                   "6-Infuriation.gif"]


def haru_expression_gui():
    """Launch expressions UI."""

    layout = [[sg.Text("Hello.")],
              [sg.pin(sg.Listbox(values=['Welcome Drink', 'Extra Cushions', 'Organic Diet','Blanket', 'Neck Rest'],
                                 select_mode='extended', key='items', size=(30, 6), visible=False)),
               sg.pin(sg.Image(background_color='white', size = (392,468), key="haru", right_click_menu=["unused", ["Quit", "Next"]]))]
              ]

    window = sg.Window("HARU Expressions", size=(530, 600)).Layout(layout)
    state = ExpressionsState(_IMAGE_SEQUENCE)
    sensor = PhidgetDialSensorManager()
    setup_callbacks(position=state.next_image, state=state.change_state)

    try:
        while True:
            event, values = window.Read(timeout=5)  # every 100ms, fire the event sg.TIMEOUT_KEY

            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break
            elif event == sg.TIMEOUT_KEY:
                if state.image_state:
                    if not window["haru"].visible:
                        window["haru"].update(visible=True)
                        window["items"].update(visible=False)
                    data = state.frame_data()
                    window["haru"].update(data)
                else:
                    window["haru"].update(visible=False)
                    window["items"].update(visible=True)

            elif event == "Next":
                if state.image_state:
                    state.next_image()
    except:
        logger.exception("UI failed")
    finally:
        sensor.close()
        window.close()


class ExpressionsState:
    """Class to maanger the state of the expression images."""

    def __init__(self, images):
        """Setup the manager"""
        self.images = [Image.open(Path(__file__).parent / "static"/ image_name) for image_name in images]
        self.image_index = 0
        self.frame_index = 0
        self.frames = self.images[self.image_index].n_frames

        self.image_state = True
        self.data = b''

    def next_image(self, value=1):
        """Move to the next image."""
        if self.image_state:
            self.frame_index = 0
            logger.debug(f"moving by {value}")
            self.image_index = (self.image_index + value) % len(self.images)
            self.frames = self.images[self.image_index].n_frames

    def frame_data(self):
        """Return the frame data."""
        image = self.images[self.image_index]
        try:
            image.seek(self.frame_index)
            self.data = _image_to_data(image)
        except (EOFError, OSError):  # OSError: broken data stream when reading image file
            pass
        self.frame_index = (self.frame_index + 1) % self.frames
        return self.data

    def change_state(self):
        self.image_state = not self.image_state


def _image_to_data(im):
    """Convert pillow.image tobyte data."""
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
        return data
