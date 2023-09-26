import arcade, arcade.gui
import main


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class MyMenu(arcade.View):
    def __init__(self):
        super().__init__()

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background
        self.background = arcade.load_texture("./risorse/image.png")

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        # --- Method 2 for handling click events,
        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start

        # --- Method 3 for handling click events,
        # use a decorator to handle on_click events
        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Settings:", event)
            self.window.show_view(SettingsMenu())

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
            )

    def on_click_start(self, event):
        game_view = main.MyGame()
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0,0, 800, 600, self.background)
        self.manager.draw()


class SettingsMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color((127, 127, 127))

        self.h_box = arcade.gui.UIBoxLayout(vertical=False)

        keyboard_button = arcade.gui.UIFlatButton(text="Keyboard", width=200)
        self.h_box.add(keyboard_button.with_space_around(right=20))

        joy_button = arcade.gui.UIFlatButton(text="Joystick", width=200)
        self.h_box.add(joy_button)

        @keyboard_button.event("on_click")
        def on_click_keyboard(event):
            print("Keyboard selected")

            f = open("input_conf.txt", "w")
            f.write("keyboard2")
            f.close()

            self.window.show_view(MyMenu())

        @joy_button.event("on_click")
        def on_click_joy(event):
            print("Joystick selected")

            f = open("input_conf.txt", "w")
            f.write("joypad")
            f.close()

            self.window.show_view(MyMenu())

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.h_box
            )
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()
