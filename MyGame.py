import arcade

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

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

        # Our physics engine
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

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

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

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

    def move_player(self, engine : arcade.PhysicsEnginePlatformer, player : arcade.Sprite, key : int):
        if key == arcade.key.UP:
            if engine.can_jump():
                player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT:
            player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            player.change_x = PLAYER_MOVEMENT_SPEED

    def stop_player(self, player : arcade.Sprite, key : int):
        if key == arcade.key.LEFT:
            player.change_x = 0
        elif key == arcade.key.RIGHT:
            player.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        self.move_player(self.physics_engine, self.player_sprite, key)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        self.stop_player(self.player_sprite, key)
        

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()


    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Draw all sprite lists in the scene
        self.scene.draw()