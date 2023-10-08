"""
Platformer Game
"""
import json
import threading

import arcade
import arcade.gui
from python_banyan.banyan_base import BanyanBase

import time

from PlayerCharacter import PlayerCharacter, PlayerCharacterJoy
import MyMenu

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
SCREEN_TITLE = "CoinCollector_1.0"
STARTING_X = 64
STARTING_Y = 128
SPRITE_SCALING = 2.5
BACKGROUND_RISE_AMOUNT = 30
MAX_LEVEL = 3
FONT_NAME = "Pixelify Sans"
FONT_FILE = "pixelify.ttf"

DMG_TIMEOUT = 1

# Constants used to scale our sprites from their original size
TILE_SCALING = 1.3
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING


# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "terreno"
LAYER_NAME_COINS = "gettoni"
LAYER_NAME_FOREGROUND = "foreground"
LAYER_NAME_BACKGROUND = "background"
LAYER_NAME_DONT_TOUCH = "no_touch"
LAYER_NAME_MOVING_PLATFORMS = "piattaforme"
LAYER_NAME_LADDERS = "scale"
ANIMATION_RESET = 15

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 1.3


class MyGame(arcade.View, threading.Thread, BanyanBase):
    """
    Main application class.
    """
    def __init__(self):

        self.custom_font = arcade.load_font(f"./risorse/font/{FONT_FILE}")

        self.event = threading.Event()

        # Opening JSON file
        with open('sample.json', 'r') as openfile:
            # Reading from json file
            self.json_conf = json.load(openfile)

        address_full = self.json_conf["address"].split(":")
        base_topic = address_full[1]

        # Call the parent class and set up the window
        arcade.View.__init__(self)
        threading.Thread.__init__(self)
        BanyanBase.__init__(self, back_plane_ip_address=address_full[0],
                            process_name="MyGame", loop_time=.001)

        self.fresh_start = True
        self.topic = base_topic
        self.subtopic = base_topic
        self.player = None
        self.platform_topic = base_topic + "platforms"
        self.button_topic = base_topic + "buttons"
        self.flag = None
        self.tile_map = None
        self.scene = None
        self.flag_anim = True
        self.counter = 0
        self.coin_anim = True

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.player_sprite2 = None
        self.hearts_sprite = None
        self.player_connected = False
        self.player_added = False

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.jump_sound2 = arcade.load_sound(":resources:sounds/jump2.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.button_activated = arcade.load_sound(":resources:sounds/hit3.wav")
        self.backgrounds = None

        # Camera
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score_player1 = 0
        self.score_player2 = 0

        # Do we need to reset the score?
        self.reset_score = True
        self.reset_score2 = True

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_show_view(self):
        self.setup()

    def setup(self):

        self.backgrounds = arcade.SpriteList()
        if self.level == 1:
            images = ("./risorse/sfondi/layers_fullcolor/sky.png",
                    "./risorse/sfondi/layers_fullcolor/far_mountains_fc.png",
                    "./risorse/sfondi/layers_fullcolor/grassy_mountains_fc.png",
                    "./risorse/sfondi/layers_fullcolor/clouds_mid_t_fc.png",
                    "./risorse/sfondi/layers_fullcolor/clouds_mid_fc.png",
                    "./risorse/sfondi/layers_fullcolor/clouds_front_fc.png",
                    "./risorse/sfondi/layers_fullcolor/clouds_front_t_fc.png")
        else:
            images = ("./risorse/sfondi/glacial_mountains/sky.png",
                      "./risorse/sfondi/glacial_mountains/clouds_bg.png",
                      "./risorse/sfondi/glacial_mountains/glacial_mountains.png",
                      "./risorse/sfondi/glacial_mountains/clouds_mg_3.png",
                      "./risorse/sfondi/glacial_mountains/clouds_mg_2.png",
                      "./risorse/sfondi/glacial_mountains/clouds_mg_1.png",
                      "./risorse/sfondi/glacial_mountains/cloud_lonely.png")

        rise = BACKGROUND_RISE_AMOUNT * SPRITE_SCALING

        for count, image in enumerate(images):
            bottom = rise * (len(images) - count - 1) 

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom 
            sprite.left = 0
            self.backgrounds.append(sprite)

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom 
            sprite.left = sprite.width
            self.backgrounds.append(sprite)

        """Set up the game here. Call this function to restart the game."""
        # Set up scene
        self.scene = arcade.Scene()

        self.level1_sound = arcade.load_sound("./risorse/music/invitation.ogg")
        self.player_sound = arcade.play_sound(self.level1_sound, looping=True)

        # Set up camera
        self.camera = arcade.Camera(self.window.width, self.window.height)

        # Out TileMap Object
        self.tile_map = None

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        # Map name
        map_name = f"./risorse/maps/livello{self.level}.json"

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

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.hearts_sprite = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(45))
        self.hearts_sprite.scale = 2
        self.hearts_sprite.center_x = 20
        self.hearts_sprite.center_y = self.window.height - 20

    def start_listening(self):
        if self.fresh_start:
            self.start()
            self.fresh_start = False
            self.set_subscriber_topic(self.subtopic)
            print(f"Sottoscritto a {self.subtopic}")

    def check_restart_player(self, player_sprite: PlayerCharacter):
        to_respawn = False
        # Did the player fall off the map?
        if player_sprite.center_y < -100:
            player_sprite.lives = 2
            self.update_hearts(player_sprite)
            player_sprite.respawn()
            arcade.play_sound(self.game_over)
            return
            
        if arcade.check_for_collision_with_list(player_sprite, self.scene[LAYER_NAME_DONT_TOUCH], method=1):
            to_respawn = True

        if time.perf_counter() - player_sprite.last_touch > DMG_TIMEOUT:
            if to_respawn:
                player_sprite.last_touch = time.perf_counter()
                player_sprite.lives -= 1
                player_sprite.isHit = True
                if player_sprite.lives == 1:
                    player_sprite.change_animation("hit")
                if player_sprite.lives == 0:
                    player_sprite.lives = 2
                    player_sprite.respawn()
                    arcade.play_sound(self.game_over)

        self.update_hearts(player_sprite)


    def run(self):
        self.receive_loop()

    def check_coin_collision(self, player_sprite: arcade.Sprite, score: int):
        coin_hit_list = arcade.check_for_collision_with_list(player_sprite, self.scene["gettoni"])

        # Loop through each coin we hit (if any) and remove it
        for count, coin in enumerate(coin_hit_list):
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            score += 1
        return score

    def check_checkpoint_collision(self, player_sprite: PlayerCharacter):
        checkpoint = arcade.check_for_collision_with_list(player_sprite, self.scene["checkpoint"])

        for flag in checkpoint:
            self.flag = flag

        if checkpoint:
            player_sprite.update_checkpoint(player_sprite.center_x, player_sprite.center_y)

    def center_camera_to_player(self, player_sprite: PlayerCharacter):
        screen_center_x = player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0 and players
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        if screen_center_x > self.tile_map.width*18:
            screen_center_x = self.tile_map.width*18
        
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

        # Update background to camera
        camera_x = self.camera.position[0]
        camera_y = self.camera.position[1]
        for count, sprite in enumerate(self.backgrounds):
            layer = count // 2
            frame = count % 2
            offset = camera_x / (2 ** (layer + 1))
            jump = (camera_x - offset) // sprite.width
            final_offset = offset + (jump + frame) * sprite.width
            sprite.left = final_offset
            sprite.bottom = camera_y

    def update_hearts(self, player_sprite):
        heart_id = 45 if player_sprite.lives == 2 else 46
        self.hearts_sprite.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(heart_id)).texture

    def draw_interface(self):
        if self.player == "P1" or (self.player == "P2" and self.player_connected):
            # Draw our score on the screen, scrolling it with the viewport
            score_text = f"Score Player 1: {self.score_player1}"
            arcade.draw_text(
                score_text,
                10,
                10,
                arcade.csscolor.WHITE,
                18,
                font_name=FONT_NAME
            )

        if self.player == "P2" or (self.player == "P1" and self.player_connected):
            score_text = f"Score Player 2: {self.score_player2}"
            arcade.draw_text(
                score_text,
                600,
                10,
                arcade.csscolor.WHITE,
                18,
                font_name=FONT_NAME
            )

        self.hearts_sprite.draw()
        

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()


        # Camera activation
        self.camera.use()

        self.backgrounds.draw(pixelated=True)

        # Draw all sprite lists in the scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        self.draw_interface()


    def animate_world(self):
        # Update flag animation
        if self.flag != None and self.counter == 0:
            if self.flag_anim:
                self.flag.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(112)).texture
                self.flag_anim = False
            else:
                self.flag.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(113)).texture
                self.flag_anim = True

        # Update coin animation
        if self.counter == 0:
            for coin in self.scene["gettoni"]:
                if self.coin_anim:
                    coin.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(152)).texture
                else:
                    coin.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(153)).texture
            self.coin_anim = not self.coin_anim
        self.counter = (self.counter + 1 ) % ANIMATION_RESET


    def check_button_collision(self, player_sprite: arcade.Sprite):
        button_hit_list = arcade.check_for_collision_with_list(player_sprite, self.scene["attivabili"])

        for count, button in enumerate(button_hit_list):
            button.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(108)).texture
            arcade.play_sound(self.button_activated)

            self.scene["attivabili"].remove(button)
            self.scene["foreground"].append(button)


    def check_level_switch(self):
        # Switch to the next level
        if len(self.scene["gettoni"]) == 0:
            # Advance to the next level
            self.level += 1

            # stop music when a new level is generated
            arcade.stop_sound(self.player_sound)

            # start from mymenu when levels are finished
            if self.level == MAX_LEVEL:
                self.window.show_view(MyMenu.MyMenu())
                return

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

            # Load the next level
            self.setup()


class MyGameP1(MyGame):
    def __init__(self):
        super().__init__()

        self.player = "P1"
        self.topic = self.topic + "P1"
        self.subtopic = self.subtopic + "P2"

    def incoming_message_processing(self, topic, payload):
        if not self.player_connected:
            self.player_connected = True

        if self.external_message_processor:
            self.external_message_processor(topic, payload)

        self.player_sprite2.center_x = payload["x"]
        self.player_sprite2.center_y = payload["y"]
        self.player_sprite2.change_x = payload["change_x"]
        self.player_sprite2.change_y = payload["change_y"]

    def setup(self):
        super().setup()

        kwargs = {
            "center_x": STARTING_X,
            "center_y": STARTING_Y,
            "platforms": self.scene[LAYER_NAME_MOVING_PLATFORMS],
            "gravity_constant": GRAVITY,
            "ladders": self.scene[LAYER_NAME_LADDERS],
            "walls": self.scene[LAYER_NAME_PLATFORMS]
        }

        self.player_sprite2 = PlayerCharacter(character="masked",
                                              keymap_conf="keyboard2",
                                              **kwargs)

        if self.json_conf["controls"] == "joypad\n":
            self.player_sprite = PlayerCharacterJoy(character="frog",
                                                    keymap_conf="keyboard1",
                                                    **kwargs)
            self.scene.add_sprite("Player", self.player_sprite)
        else:
            self.player_sprite = PlayerCharacter(character="frog",
                                                 keymap_conf="keyboard1",
                                                 **kwargs)
            self.scene.add_sprite("Player", self.player_sprite)

        self.hearts = self.player_sprite.lives

        self.start_listening()

    def on_key_press(self, key: int, modifiers: int):
        """ Called whenever a key is pressed """
        self.player_sprite.notify_keypress(key)

        if key == arcade.key.ESCAPE:
            arcade.stop_sound(self.player_sound)
            self.clean_up()
            self.window.show_view(MyMenu.MyMenu())

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        self.player_sprite.notify_keyrelease(key)

    def check_button_collision(self, player_sprite: arcade.Sprite):
        button_hit_list = arcade.check_for_collision_with_list(player_sprite, self.scene["attivabili"])

        for count, button in enumerate(button_hit_list):
            button.texture = self.tile_map._create_sprite_from_tile(self.tile_map._get_tile_by_gid(108)).texture
            arcade.play_sound(self.button_activated)

            piattaforma = button.properties["piattaforma"]
            for platform in self.scene["piattaforme"]:
                if platform.properties["attivabile"] == piattaforma:
                    if platform.properties["moving"] == 1:
                        platform.change_y = 0.5
                    elif platform.properties["moving"] == 0:
                        platform.change_x = 0.5
                    self.scene["attivabili"].remove(button)
                    self.scene["foreground"].append(button)

    def on_update(self, delta_time: float):
        """Movement and game logic"""

        if self.player_connected and not self.player_added:
            self.scene.add_sprite("Player", self.player_sprite2)
            self.player_added = True

        self.player_sprite.update_character()
        self.player_sprite2.update_animation()

        # Position the camera
        self.center_camera_to_player(self.player_sprite)

        self.score_player1 = self.check_coin_collision(self.player_sprite, self.score_player1)
        self.score_player2 = self.check_coin_collision(self.player_sprite2, self.score_player2)
        self.check_button_collision(self.player_sprite)
        self.check_button_collision(self.player_sprite2)
        self.check_checkpoint_collision(self.player_sprite)
        self.check_restart_player(self.player_sprite)
        
        self.animate_world()

        # Update walls, used with moving platforms
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        # Publish player and world updates
        payload = {
            "x": self.player_sprite.center_x,
            "y": self.player_sprite.center_y,
            "change_x": self.player_sprite.change_x,
            "change_y": self.player_sprite.change_y
        }
    
        self.publish_payload(payload, self.topic)

        for count, platform in enumerate(self.scene["piattaforme"]):
            self.publish_payload({"idx": count, "c_x": platform.center_x, "c_y": platform.center_y}, self.platform_topic)

        self.check_level_switch()


class MyGameP2(MyGame):
    def __init__(self):
        super().__init__()

        self.player = "P2"
        self.topic = self.topic + "P2"
        self.subtopic = self.subtopic + "P1"

    def incoming_message_processing(self, topic, payload):
        if not self.player_connected:
            self.player_connected = True

        if self.external_message_processor:
            self.external_message_processor(topic, payload)

        if topic == self.subtopic:
            self.player_sprite.center_x = payload["x"]
            self.player_sprite.center_y = payload["y"]
            self.player_sprite.change_x = payload["change_x"]
            self.player_sprite.change_y = payload["change_y"]
        elif topic == self.platform_topic:
            idx = payload["idx"]
            self.scene["piattaforme"][idx].center_x = payload["c_x"]
            self.scene["piattaforme"][idx].center_y = payload["c_y"]

    def setup(self):
        super().setup()

        kwargs = {
            "center_x": STARTING_X,
            "center_y": STARTING_Y,
            "platforms": self.scene[LAYER_NAME_MOVING_PLATFORMS],
            "gravity_constant": GRAVITY,
            "ladders": self.scene[LAYER_NAME_LADDERS],
            "walls": self.scene[LAYER_NAME_PLATFORMS]
        }

        self.player_sprite = PlayerCharacter(character="frog",
                                             keymap_conf="keyboard2",
                                             **kwargs)

        if self.json_conf["controls"] == "joypad\n":
            self.player_sprite2 = PlayerCharacterJoy(character="masked",
                                                     keymap_conf="keyboard1",
                                                     **kwargs)
            self.scene.add_sprite("Player", self.player_sprite2)
        else:
            self.player_sprite2 = PlayerCharacter(character="masked",
                                                  keymap_conf="keyboard1",
                                                  **kwargs)
            self.scene.add_sprite("Player", self.player_sprite2)

        self.hearts = self.player_sprite2.lives

        if self.fresh_start:
            self.set_subscriber_topic(self.platform_topic)
        self.start_listening()


    def on_key_press(self, key: int, modifiers: int):
        """ Called whenever a key is pressed """
        self.player_sprite2.notify_keypress(key)

        if key == arcade.key.ESCAPE:
            arcade.stop_sound(self.player_sound)
            self.clean_up()
            self.window.show_view(MyMenu.MyMenu())


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        self.player_sprite2.notify_keyrelease(key)


    def on_update(self, delta_time: float):
        """Movement and game logic"""

        if self.player_connected and not self.player_added:
            self.scene.add_sprite("Player", self.player_sprite)
            self.player_added = True

        self.player_sprite.update_animation()
        self.player_sprite2.update_character()

        # Position the camera
        self.center_camera_to_player(self.player_sprite2)

        self.score_player1 = self.check_coin_collision(self.player_sprite, self.score_player1)
        self.score_player2 = self.check_coin_collision(self.player_sprite2, self.score_player2)
        self.check_button_collision(self.player_sprite)
        self.check_button_collision(self.player_sprite2)
        self.check_checkpoint_collision(self.player_sprite2)
        self.check_restart_player(self.player_sprite2)

        self.animate_world()


        # Update walls, used with moving platforms
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])
        
        payload = {
            "x": self.player_sprite2.center_x,
            "y": self.player_sprite2.center_y,
            "change_x": self.player_sprite2.change_x,
            "change_y": self.player_sprite2.change_y
        }
        self.publish_payload(payload, self.topic)

        self.check_level_switch()


def main():
    """Main function"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MyMenu.MyMenu())
    arcade.run()


if __name__ == "__main__":
    main()
