"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5


# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, weith, heigth, title):

        # Call the parent class and set up the window
        super().__init__(weith, heigth, title)

        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

# Our pysics engine
        self.physics_engine = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Set up scene
        self.scene = arcade.Scene()

        # Add sprite lists to scene object
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")
      

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/robot/robot_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        image_source = ":resources:images/animated_characters/zombie/zombie_idle.png/"
        self.player_sprite2 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite2.center_x = self.player_sprite.center_x + self.player_sprite.width/2
        self.player_sprite2.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite2)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        #Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )
        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            # Add a crate on the ground
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)
    
    
    def on_key_press(self, symbol: int, modifiers: int):
        """ Called whenever a key is pressed """
        if symbol ==arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif symbol ==arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    
    def on_update(self, delta_time: float):
        """Movement and game logic"""
        
        # Move the player with the physics engine
        self.physics_engine.update()


    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Draw all sprite lists in the scene
        self.scene.draw()


def main():
    """Main function"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()