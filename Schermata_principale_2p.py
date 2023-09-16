"""
Platformer Game
"""
import arcade
from MyGame import MyGame

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5


# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

class MyGame2P(MyGame):
    """
    Main application class.
    """

    def __init__(self, weith, heigth, title):

        # Call the parent class and set up the window
        super().__init__(weith, heigth, title)

        self.player_sprite2 = None
        self.physics_engine2 = None


    def setup(self):
        super().setup()
        image_source = ":resources:images/animated_characters/zombie/zombie_idle.png/"
        self.player_sprite2 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite2.center_x = self.player_sprite.center_x + self.player_sprite.width/2
        self.player_sprite2.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite2)

        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )


    def on_key_press(self, key: int, modifiers: int):
        super().on_key_press(key, modifiers)

        if key == arcade.key.W:
            if self.physics_engine2.can_jump():
                self.player_sprite2.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.A:
            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED


    def on_key_release(self, key, modifiers):
        super().on_key_release(key, modifiers)
        if key == arcade.key.A:
            self.player_sprite2.change_x = 0
        elif key == arcade.key.D:
            self.player_sprite2.change_x = 0
    

    def on_update(self, delta_time: float):
        super().on_update(delta_time)
        self.physics_engine2.update()


def main():
    """Main function"""
    window = MyGame2P(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()