"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5


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

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Keep track of the score
        self.score_player1 = 0
        self.score_player2 = 0

        # Add sprite lists to scene object
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")

        # Use a loop to place some coins for our character to pick up
        for x in range(128, 1250, 256):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = 96
            self.scene.add_sprite("Coins", coin)
        
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
    
    
        #Create the 'physics engine'

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2, gravity_constant=GRAVITY, walls=self.scene["Walls"]
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
       
        # Position the camera
        self.center_camera_to_player()

        # Move the player with the physics engine
        self.physics_engine.update()
        self.physics_engine2.update()

         # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        coin_hit_list2 = arcade.check_for_collision_with_list(
            self.player_sprite2, self.scene["Coins"]
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
        if self.camera.position[0] + self.camera.viewport_width < (self.player_sprite2.center_x + self.player_sprite2.width/2):
             if self.player_sprite.change_x < 0: 
                self.player_sprite.change_x = 0
             if self.player_sprite2.change_x > 0: 
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