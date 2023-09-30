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

        self.v_box = arcade.gui.UIBoxLayout()
        self.h_box = arcade.gui.UIBoxLayout(vertical=False)
        self.player_selection = arcade.gui.UIBoxLayout(vertical=False)

        keyboard_button = arcade.gui.UIFlatButton(text="Keyboard", width=200)
        self.h_box.add(keyboard_button.with_space_around(right=20))

        joy_button = arcade.gui.UIFlatButton(text="Joystick", width=200)
        self.h_box.add(joy_button)

        p1_button = arcade.gui.UIFlatButton(text="P1", width=200)
        self.player_selection.add(p1_button.with_space_around(right=20))

        p2_button = arcade.gui.UIFlatButton(text="P2", width=200)
        self.player_selection.add(p2_button)

        save_button = arcade.gui.UIFlatButton(text="Save", width=200)

        self.v_box.add(self.h_box.with_space_around(bottom=20))
        self.v_box.add(self.player_selection.with_space_around(bottom=20))
        self.v_box.add(save_button)

        self.controls_choice = "keyboard2\n"
        self.player_choice = "P1\n"

        @keyboard_button.event("on_click")
        def on_click_keyboard(event):
            print("Keyboard selected")
            self.controls_choice = "keyboard2\n"

        @joy_button.event("on_click")
        def on_click_joy(event):
            print("Joystick selected")
            self.controls_choice = "joypad\n"

        @p1_button.event("on_click")
        def on_click_p1(event):
            print("Playing as P1")
            self.player_choice = "P1\n"

        @p2_button.event("on_click")
        def on_click_p2(event):
            print("Playing as P2")
            self.player_choice = "P2\n"

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.h_box
            )
        )

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

        @save_button.event("on_click")
        def save_conf(event):
            f = open("input_conf.txt", "w")
            f.write(self.controls_choice)
            f.write(self.player_choice)
            f.close()
            self.window.show_view(MyMenu())

    def on_draw(self):
        self.clear()
        self.manager.draw()
