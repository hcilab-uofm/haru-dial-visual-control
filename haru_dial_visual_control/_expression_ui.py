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
              [sg.Image(background_color='white', size = (392,468), key="haru", right_click_menu=["unused", ["Quit", "Next"]])]]

    window = sg.Window("HAL 220").Layout(layout)
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
                    data = state.frame_data()
                    window["haru"].update(data)
                else:
                    # TODO: What happens here?

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

    def next_image(self):
        """Move to the next image."""
        self.frame_index = 0
        self.image_index = (self.image_index + 1) % len(self.images)
        self.frames = self.images[self.image_index].n_frames

    def frame_data(self):
        """Return the frame data."""
        image = self.images[self.image_index]
        image.seek(self.frame_index)
        data = _image_to_data(image)
        self.frame_index = (self.frame_index + 1) % self.frames
        return data

    def change_state(self):
        self.image_state = not self.image_state


def _image_to_data(im):
    """Convert pillow.image tobyte data."""
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data
