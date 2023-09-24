import arcade
import pyglet

# Disable xinput controllers otherwise joystick is recognized
# as input device
pyglet.options["xinput_controllers"] = False


class PlayerInputJoystick:

    def __init__(self):
        # Get list of game controllers that are available
        joysticks = arcade.get_joysticks()

        self.change_x = 0
        self.change_y = 0
        self.button = -1

        # If we have any...
        if joysticks:
            # Grab the first one in  the list
            self.joystick = joysticks[0]

            # Open it for input
            self.joystick.open()

            # Push this object as a handler for joystick events.
            # Required for the on_joy* events to be called.
            self.joystick.push_handlers(self)
        else:
            # Handle if there are no joysticks.
            print("There are no joysticks, plug in a joystick and run again.")
            self.joystick = None

    def get_change(self):
        # If there is a joystick, grab the speed.
        if self.joystick:
            # x-axis
            self.change_x = self.joystick.x
            # Set a "dead zone" to prevent drive from a centered joystick
            if abs(self.change_x) < 0.5:
                self.change_x = 0

        self.change_y = 1 if self.button == 0 else 0
        self.button = -1

        return self.change_x, self.change_y

    # noinspection PyMethodMayBeStatic
    def on_joybutton_press(self, _joystick, button):
        """ Handle button-down event for the joystick """
        print("Button {} down".format(button))
        self.button = button

    # noinspection PyMethodMayBeStatic
    def on_joybutton_release(self, _joystick, button):
        """ Handle button-up event for the joystick """
        print("Button {} up".format(button))

    # noinspection PyMethodMayBeStatic
    def on_joyhat_motion(self, _joystick, hat_x, hat_y):
        """ Handle hat events """
        print("Hat ({}, {})".format(hat_x, hat_y))