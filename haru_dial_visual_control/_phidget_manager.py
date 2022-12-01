from loguru import logger
from Phidget22.Devices.Encoder import Encoder
from Phidget22.Devices.DigitalInput import DigitalInput


def _on_position_change(self, positionChange, timeChange, indexTriggered):
    logger.debug("PositionChange: " + str(positionChange))
    logger.debug("TimeChange: " + str(timeChange))
    logger.debug("IndexTriggered: " + str(indexTriggered))
    logger.debug("getPosition: " + str(self.getPosition()))
    logger.debug("----------")


def _on_attach(self):
    logger.debug("Attach!")


def _on_detach(self):
    logger.debug("Detach!")


def _on_error(self, code, description):
    logger.debug("Code: " + ErrorEventCode.getName(code))
    logger.debug("Description: " + str(description))
    logger.debug("----------")


def _on_state_change(self, state):
    logger.debug("State: " + str(state))


class PhidgetDialSensorManager:
    """Handles the dial sensor."""

    def __init__(self):
        """Confiure sensor."""
        try:
            self.encoder0 = Encoder()
            self.digitalInput0 = DigitalInput()

            #Assign any event handlers you need before calling open so that no events are missed.
            self.encoder0.setOnPositionChangeHandler(_on_position_change)
            self.encoder0.setOnAttachHandler(_on_attach)
            self.encoder0.setOnDetachHandler(_on_detach)
            self.encoder0.setOnErrorHandler(_on_error)
            self.digitalInput0.setOnStateChangeHandler(_on_state_change)
            self.digitalInput0.setOnAttachHandler(_on_attach)
            self.digitalInput0.setOnDetachHandler(_on_detach)
            self.digitalInput0.setOnErrorHandler(_on_error)

            #Open your Phidgets and wait for attachment
            self.encoder0.openWaitForAttachment(5000)
            self.digitalInput0.openWaitForAttachment(5000)

            self.encoder0.setPositionChangeTrigger(1)
        except:
            logger.exception("Sensor init failed.")
            self.encoder0 = None
            self.digitalInput0 = None

    def wait(self):
        """Wait for enter to stop."""
        try:
            input("Press Enter to Stop\n")
        except (Exception, KeyboardInterrupt):
            self.close()

    def close(self):
        """Close sensor."""
        if self.encoder0 is not None:
            self.encoder0.close()
        if self.digitalInput0 is not None:
            self.digitalInput0.close()
