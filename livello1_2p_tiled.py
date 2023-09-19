"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.5
TILE_SCALING = 1.3
COIN_SCALING = 0.5


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

        # Our pysics engine
        self.physics_engine = None

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.jump_sound2 = arcade.load_sound(":resources:sounds/jump2.wav")


        #Camera
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score_player1 = 0
        self.score_player2 = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Set up scene
        self.scene = arcade.Scene()

        #Set up camera
        self.camera = arcade.Camera(self.width, self.height)

        # Out TileMap Object
        self.tile_map = None

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = "./risorse/livello1.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            "terreno": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        # Keep track of the score
        self.score_player1 = 0
        self.score_player2 = 0
        
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

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
    
    
        #Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["terreno"]
        )

        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2, gravity_constant=GRAVITY, walls=self.scene["terreno"]
        )


    def on_key_press(self, symbol: int, modifiers: int):
        """ Called whenever a key is pressed """

        if symbol == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)
        elif symbol ==arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.W:
            if self.physics_engine2.can_jump():
                self.player_sprite2.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound2)
        elif symbol ==arcade.key.A:
            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.D:
            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0


        if key == arcade.key.W:
            self.player_sprite2.change_y = 0
        elif key == arcade.key.A:
            self.player_sprite2.change_x = 0
        if key == arcade.key.D:
            self.player_sprite2.change_x = 0


    def on_update(self, delta_time: float):
        """Movement and game logic"""
       
        print(self.camera.position, self.player_sprite2.center_x - self.player_sprite2.width/2)

        # Position the camera
        self.center_camera_to_player()

        # Move the player with the physics engine
        self.physics_engine.update()
        self.physics_engine2.update()

         # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["gettoni"]
        )

        coin_hit_list2 = arcade.check_for_collision_with_list(
            self.player_sprite2, self.scene["gettoni"]
        )
        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            self.score_player1 += 1

        for coin in coin_hit_list2:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            self.score_player2 += 1

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        # Don't let camera travel past 0 and players
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_x > (self.player_sprite2.center_x - self.player_sprite2.width/2):
            screen_center_x = (self.player_sprite2.center_x - self.player_sprite2.width/2) 

        if self.camera.position[0] + self.camera.viewport_width < (self.player_sprite.center_x + self.player_sprite.width/2):
            if self.player_sprite.change_x > 0: 
                self.player_sprite.change_x = 0
            if self.player_sprite2.change_x < 0:
                self.player_sprite2.change_x = 0
        if self.camera.position[0] > (self.player_sprite.center_x - self.player_sprite.width/2):
            if self.player_sprite.change_x < 0: 
                self.player_sprite.change_x = 0
        if self.camera.position[0] + self.camera.viewport_width < (self.player_sprite2.center_x + self.player_sprite2.width/2):
             if self.player_sprite2.change_x > 0: 
                self.player_sprite2.change_x = 0
        if self.camera.position[0] > (self.player_sprite2.center_x - self.player_sprite2.width/2 + PLAYER_MOVEMENT_SPEED):
             if self.player_sprite2.change_x < 0: 
                self.player_sprite2.change_x = 0

        player_centered = screen_center_x, screen_center_y

        

        self.camera.move_to(player_centered)

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        #Camera activation
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