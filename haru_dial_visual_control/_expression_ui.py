import os
from io import BytesIO
from pathlib import Path
from typing import Dict

import PySimpleGUI as sg
import pyttsx3
from PIL import Image
from loguru import logger

from haru_dial_visual_control._phidget_manager import PhidgetDialSensorManager, setup_callbacks


_IMAGE_SEQUENCE = {
    "02-saddened.gif":           "pick what you would like to do",
    "07-sad.gif":                "pick what you would like to do",
    "10-suprised.gif":           "pick what you would like to do",
    "11-joy.gif":                "pick what you would like to do",
    "16-heart-eyes.gif":         "pick what you would like to do",
    "2-tongue_sticking_out.gif": "Great to see you are feeling playful"
}


_MENU_ITEMS = {"Play a game": "Go outside kido!",
               "Play with a friend": "You need friends?",
               "play with a kid nearby": "go outside",
               "play with parent": "call your mother"}


def haru_expression_gui():
    """Launch expressions UI."""
    sg.theme("DarkBrown1")

    menu_items = [[sg.Button(it, font=("Times New Roman", 22, "bold"),
                             expand_x=True, expand_y=True, size=(55, 3), key=it),] for it in _MENU_ITEMS.keys()]

    layout = [[sg.Text("Hi.\nRotate the dial and press down on the one you like", font=("Times New Roman", 12)), sg.Push(), sg.pin(sg.Button("Restart", key="restart"))],
              [sg.pin(sg.Column(menu_items, visible=False, key="items", element_justification="center")),
               sg.pin(sg.Text("booooo", font=("Times New Roman", 55, "bold"), key="final_text", visible=False)),
               sg.pin(sg.Image(background_color='white', size=(392, 468), key="haru", right_click_menu=["unused", ["Select this", "Next", "Quit"]]))]
              ]

    window = sg.Window("HARU Expressions", layout=layout, size=(530, 600), finalize=True)

    # Setting up states, and the pidget sensor
    state = ExpressionsState(_IMAGE_SEQUENCE, _MENU_ITEMS)
    sensor = PhidgetDialSensorManager()
    setup_callbacks(position=state.next_value, state=state.change_state)

    # Configure tts
    tts_engine = pyttsx3.init()

    if os.name == "nt":
        tts_engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")

    rate = tts_engine.getProperty('rate')
    tts_engine.setProperty('rate', rate - 50)

    # Setting up the focus events

    default_button_color = None
    
    for item in menu_items:
        item[0].bind('<FocusIn>', '+FOCUS IN+')
        item[0].bind('<FocusOut>', '+FOCUS OUT+')
        default_button_color = item[0].ButtonColor

    try:
        while True:
            event, values = window.Read(timeout=1)  # every 100ms, fire the event sg.TIMEOUT_KEY

            if event != sg.TIMEOUT_KEY:
                logger.debug("Event: {event}, {values}")

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
                        tts_engine.say(state.images_data[state.image_index][1])
                        tts_engine.runAndWait()
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
                        tts_engine.say(state.menu_items[state.menu_key()])
                        tts_engine.runAndWait()

            elif event == "Next":
                state.next_value()

            elif event == "restart":
                state.reset()
                logger.debug("Restarting process")

            elif event == "Select this":
                state.change_state()
                
            elif event in state.menu_items:
                window["haru"].update(visible=False)
                window["items"].update(visible=False)
                window["final_text"].update(visible=True)

                window["final_text"].update(value=state.menu_items[event])
                tts_engine.say(state.menu_items[event])
                tts_engine.runAndWait()

            elif "+FOCUS IN+" in event:
                window[event.rstrip("+FOCUS IN+")].update(button_color=default_button_color[::-1])

            elif "+FOCUS OUT+" in event:
                window[event.rstrip("+FOCUS OUT+")].update(button_color=default_button_color)

    except:
        logger.exception("UI failed")
    finally:
        sensor.close()
        window.close()


class ExpressionsState:
    """Class to maanger the state of the expression images."""

    def __init__(self, images: Dict[str, str], menu_items: Dict[str, str]) -> None:
        """Setup the manager."""
        self.images_data = list(images.items())
        self.images = [Image.open(Path(__file__).parent / "static"/ image_name) for image_name, _ in self.images_data]
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

    def get_state_changed(self) -> bool:
        """Return if change has happened to state. Resets state if read."""
        ret_val = self._state_changed
        self._state_changed = False
        return ret_val

    def get_value_changed(self) -> bool:
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

    def change_state(self, state=None) -> None:
        """Change the state."""
        _state = self.state
        if state is not None:
            self.state = state
        elif self.state == "image":
            self.state = "menu"
        elif self.state == "menu":
            self.state = "text"
        else:
            self.state = "text"

        if _state != self.state:
            self._state_changed = True

    def reset(self):
        self.change_state("image")


def _image_to_data(im):
    """Convert pillow.image tobyte data."""
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
        return data
