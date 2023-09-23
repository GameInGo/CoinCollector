"""
Platformer Game
"""

import arcade
from PlayerCharacter import PlayerCharacter

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.5
TILE_SCALING = 1.3
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player starting position
PLAYER_START_X = 64
PLAYER_START_Y = 225

# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "terreno"
LAYER_NAME_COINS = "gettoni"
LAYER_NAME_FOREGROUND = "foreground"
LAYER_NAME_BACKGROUND = "background"
LAYER_NAME_DONT_TOUCH = "no_touch"
LAYER_NAME_MOVING_PLATFORMS = "piattaforme"
LAYER_NAME_LADDERS = "scale"

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 1.3
PLAYER_JUMP_SPEED = 15


class MyGame(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, weith, heigth, title):

        # Call the parent class and set up the window
        super().__init__(weith, heigth, title)
        self.tile_map = None
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.player_sprite2 = None

        # Our pysics engine
        self.physics_engine = None
        self.physics_engine2 = None

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.jump_sound2 = arcade.load_sound(":resources:sounds/jump2.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

        # Camera
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Do we need to reset the score?
        self.reset_score = True
        self.reset_score2 = True

        # Keep track of the score
        self.score_player1 = 0
        self.score_player2 = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Set up scene
        self.scene = arcade.Scene()

        level1_sound = arcade.load_sound("./risorse/music/invitation.ogg")
        arcade.play_sound(level1_sound, looping=True)

        # Set up camera
        self.camera = arcade.Camera(self.width, self.height)

        # Out TileMap Object
        self.tile_map = None

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Map name
        map_name = f"./risorse/livello{self.level}.json"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Calculate the right edge of the my_map in pixels
        # TODO: GRID_PIXEL_SIZE è troppo grande come misura
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE * 1000

        # Keep track of the score, make sure we keep the score if the player finishes a level
        if self.reset_score:
            self.score_player1 = 0
        if self.reset_score2:
            self.score_player2 = 0

        self.reset_score = True
        self.reset_score2 = True

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter(character="frog")
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.player_sprite2 = PlayerCharacter(character="masked")
        self.player_sprite2.center_x = self.player_sprite.center_x + self.player_sprite.width/2
        self.player_sprite2.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite2)

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
    
        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS])
        
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS])

    def on_key_press(self, symbol: int, modifiers: int):
        """ Called whenever a key is pressed """

        if symbol == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif symbol == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.W:
            if self.physics_engine2.can_jump():
                self.player_sprite2.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound2)
        elif symbol == arcade.key.A:
            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.D:
            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.A:
            self.player_sprite2.change_x = 0
        if key == arcade.key.D:
            self.player_sprite2.change_x = 0

    def check_coin_collision(self, player_sprite: arcade.Sprite, score: int):
        coin_hit_list = arcade.check_for_collision_with_list(player_sprite, self.scene["gettoni"])
        
        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            score += 1
            
        return score

    def check_restart_player(self, player_sprite: arcade.Sprite):
        # Did the player fall off the map?
        if player_sprite.center_y < -100:
            player_sprite.center_x = PLAYER_START_X
            player_sprite.center_y = PLAYER_START_Y

            arcade.play_sound(self.game_over)

        # # Did the player touch something they should not?
        if arcade.check_for_collision_with_list(player_sprite, self.scene[LAYER_NAME_DONT_TOUCH], method=1):
            player_sprite.change_x = 0
            player_sprite.change_y = 0
            player_sprite.center_x = PLAYER_START_X
            player_sprite.center_y = PLAYER_START_Y

            arcade.play_sound(self.game_over)

    def on_update(self, delta_time: float):
        """Movement and game logic"""

        # Position the camera
        self.center_camera_to_player()

        self.player_sprite.update_animation()
        self.player_sprite2.update_animation()

        # Move the player with the physics engine
        self.physics_engine.update()
        self.physics_engine2.update()

        self.score_player1 = self.check_coin_collision(self.player_sprite, self.score_player1)
        self.score_player2 = self.check_coin_collision(self.player_sprite2, self.score_player2)

        self.check_restart_player(self.player_sprite)
        self.check_restart_player(self.player_sprite2)

        # Update walls, used with moving platforms
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

            # Load the next level
            self.setup()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0 and players
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_x > (self.player_sprite2.center_x - self.player_sprite2.width/2):
            screen_center_x = (self.player_sprite2.center_x - self.player_sprite2.width/2) 

        if (self.camera.position[0] + self.camera.viewport_width <
                (self.player_sprite.center_x + self.player_sprite.width/2)):
            if self.player_sprite.change_x > 0: 
                self.player_sprite.change_x = 0
            if self.player_sprite2.change_x < 0:
                self.player_sprite2.change_x = 0
        if self.camera.position[0] > (self.player_sprite.center_x - self.player_sprite.width/2):
            if self.player_sprite.change_x < 0: 
                self.player_sprite.change_x = 0
        if (self.camera.position[0] + self.camera.viewport_width <
                (self.player_sprite2.center_x + self.player_sprite2.width/2)):
            if self.player_sprite2.change_x > 0:
                self.player_sprite2.change_x = 0
        if (self.camera.position[0] >
                (self.player_sprite2.center_x - self.player_sprite2.width/2 + PLAYER_MOVEMENT_SPEED)):
            if self.player_sprite2.change_x < 0:
                self.player_sprite2.change_x = 0

        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Camera activation
        self.camera.use()

        # Draw all sprite lists in the scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score Player 1: {self.score_player1}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )

        score_text = f"Score Player 2: {self.score_player2}"
        arcade.draw_text(
            score_text,
            600,
            10,
            arcade.csscolor.WHITE,
            18,
        )


def main():
    """Main function"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
