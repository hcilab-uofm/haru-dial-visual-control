from typing import List, Dict
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


_MENU_ITEMS = {"Val 1": "saying one",
               "Val 2": "saying 2",
               "Val 3": "saying three",
               "Val 4": "saying power",
               "Val 5": "saying moo"}


def haru_expression_gui():
    """Launch expressions UI."""
    menu_items = [[sg.Button(it, font=("Times New Roman", 12),
                             expand_x=True, expand_y=True, size=(55, 3), key=it),] for it in _MENU_ITEMS.keys()]

    layout = [[sg.Text("Hello.")],
              [sg.pin(sg.Column(menu_items, visible=False, key="items", element_justification="center")),
               sg.pin(sg.Text("booooo", font=("Times New Roman", 25), key="final_text", visible=False)),
               sg.pin(sg.Image(background_color='white', size=(392, 468), key="haru", right_click_menu=["unused", ["Quit", "Next"]]))]
              ]

    window = sg.Window("HARU Expressions", size=(530, 600)).Layout(layout)
    state = ExpressionsState(_IMAGE_SEQUENCE, _MENU_ITEMS)
    sensor = PhidgetDialSensorManager()
    setup_callbacks(position=state.next_value, state=state.change_state)

    try:
        while True:
            event, values = window.Read(timeout=5)  # every 100ms, fire the event sg.TIMEOUT_KEY

            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break
            elif event == sg.TIMEOUT_KEY:
                _state_changed = state.get_state_changed()
                _value_changed = state.get_value_changed()
                if state.state == "image":
                    # Ensure the correct elements is visible
                    if _state_changed and not window["haru"].visible:
                        window["haru"].update(visible=True)
                        window["items"].update(visible=False)
                        window["final_text"].update(visible=False)

                    # Value change is handled by the callbacks
                    # Just display the right element
                    data = state.frame_data()
                    window["haru"].update(data)
                elif state.state == "menu":
                    # Ensure the correct elements is visible
                    if _state_changed and not window["items"].visible:
                        window["haru"].update(visible=False)
                        window["items"].update(visible=True)
                        window["final_text"].update(visible=False)

                    if _value_changed:
                        current_key = state.menu_key()
                        for key in state.menu_keys:
                            if key == current_key:
                                window[key].set_focus(force=True)

                elif state.state == "text":
                    # Ensure the correct elements is visible
                    if _state_changed and not window["final_text"].visible:
                        window["haru"].update(visible=False)
                        window["items"].update(visible=False)
                        window["final_text"].update(visible=True)

                        window["final_text"].update(value=state.menu_items[state.menu_key()])

            elif event == "Next":
                state.next_value()
    except:
        logger.exception("UI failed")
    finally:
        sensor.close()
        window.close()


class ExpressionsState:
    """Class to maanger the state of the expression images."""

    def __init__(self, images: List[str], menu_items: Dict[str, str]) -> None:
        """Setup the manager."""
        self.images = [Image.open(Path(__file__).parent / "static"/ image_name) for image_name in images]
        self.image_index = 0
        self.frame_index = 0
        self.frames = self.images[self.image_index].n_frames

        self.state = "image"  # "menu", "text"
        self.data = b''

        self.menu_items = menu_items
        self.menu_keys = list(menu_items.keys())
        self._current_menu_index = 0

        self._value_changed = False
        self._state_changed = False

    def next_value(self, value: int = 1) -> None:
        """Move to the next image."""
        if self.state == "image":
            self.frame_index = 0
            logger.debug(f"moving by {value}")
            self.image_index = (self.image_index + value) % len(self.images)
            self.frames = self.images[self.image_index].n_frames
        elif self.state == "menu":
            self._current_menu_index = (self._current_menu_index + value) % len(self.menu_keys)
        else:
            pass

        self._value_changed = True

    def get_state_changed(self) -> None:
        """Return if change has happened to state. Resets state if read."""
        ret_val = self._state_changed
        self._state_changed = False
        return ret_val

    def get_value_changed(self) -> None:
        """Return if change has happened to value. Resets state if read."""
        ret_val = self._value_changed
        self._value_changed = False
        return ret_val

    def frame_data(self) -> Image.Image:
        """Return the frame data."""
        image = self.images[self.image_index]
        try:
            image.seek(self.frame_index)
            self.data = _image_to_data(image)
        except (EOFError, OSError):  # OSError: broken data stream when reading image file
            pass
        self.frame_index = (self.frame_index + 1) % self.frames
        return self.data

    def menu_key(self) -> str:
        """Return the key of the current highlight menu."""
        return self.menu_keys[self._current_menu_index]

    def change_state(self) -> None:
        """Change the state."""
        _state = self.state
        if self.state == "image":
            self.state = "menu"
        elif self.state == "menu":
            self.state = "text"
        else:
            self.state = "text"

        if _state != self.state:
            self._state_changed = True


def _image_to_data(im):
    """Convert pillow.image tobyte data."""
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
        return data
