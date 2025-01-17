This is a demo application for handling HARU visuals using [phidget dial](https://www.phidgets.com/?tier=3&catid=15&pcid=13&prodid=982)

![demo](media/demo.gif)

Demo with audio:
<video src="https://user-images.githubusercontent.com/15046660/206072831-7e76b642-384b-4b6c-bdcf-753161078d08.mp4"></video>


# Installation
1. Install and configure the phidget sensor. On the product see the `User Guide` tab. Additional examples can be found under the `Code Samples` tab.
2. Ensure the dial is working correctly with the same code or using Phidget Control Panel.
3. Install this as a package using pip:

```sh
pip install https://github.com/hcilab-uofm/haru-dial-visual-control
```

or

use the executable in the Release

# Usage
Note that the application still can be used without the sensor by interacting with the menu items.

1. Start the application by running:
```sh
haru expressions
```

or double-click on the downloaded executable.

2. Use the dial to move between animations
   - Use without pidget: right-click and select `Next`
3. Press down on the dial to toggle between the menu and images
   - Use without pidget: right-click and select `Select this`
4. Use the dial to move between items and press down to select.
   - Use without pidget: Click on the corresponding button.
5. To restart at any point click the `Restart` button
