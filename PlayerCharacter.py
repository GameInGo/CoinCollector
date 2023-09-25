import arcade
import pyglet

# Disable xinput controllers otherwise joystick is recognized
# as input device
pyglet.options["xinput_controllers"] = False

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

UPDATES_PER_FRAME = 3
CHARACTER_SCALING = 1.5

PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 3

anim_dict = {
    "idle": {
        "max_frame": 11
    },
    "run": {
        "max_frame": 12
    },
    "djump": {
        "max_frame": 5
    },
    "jump": {
        "max_frame": 1
    },
    "fall": {
        "max_frame": 1
    }
}


keymap = {
    "keyboard1": {
        "up": arcade.key.UP,
        "down": arcade.key.DOWN,
        "left": arcade.key.LEFT,
        "right": arcade.key.RIGHT
    },
    "keyboard2": {
        "up": arcade.key.W,
        "down": arcade.key.S,
        "left": arcade.key.A,
        "right": arcade.key.D
    }
}


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """

    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self, character: str, keymap_conf: str, center_x, center_y, platforms, gravity_constant, ladders, walls):
        # Set up parent class
        super().__init__()

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        self.keymap_conf = keymap_conf

        self.center_x = center_x
        self.center_y = center_y

        self.curr_anim = "idle"

        self.physics_engine = arcade.PhysicsEnginePlatformer(self, platforms, gravity_constant, ladders, walls)
        self.physics_engine.enable_multi_jump(2)

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # --- Load Textures ---
        main_path = "./risorse/assets/"
        run = f"{character}_run/{character}_run"
        idle = f"{character}_idle/{character}_idle"
        double_jump = f"{character}_double_jump/{character}_double_jump"
        jump = f"{character}_jump/{character}_jump"
        fall = f"{character}_fall/{character}_fall"

        self.anim_texture_map = {}

        # Load textures for idle standing
        self.idle_texture_pair = []
        self.add_animation(main_path, idle, "idle", self.idle_texture_pair)

        # Load textures for walking
        self.walk_textures = []
        self.add_animation(main_path, run, "run", self.walk_textures)

        # Load textures for double jumping
        self.double_jump = []
        self.add_animation(main_path, double_jump, "djump", self.double_jump)

        # Load textures for jumping
        self.jump = []
        self.add_animation(main_path, jump, "jump", self.jump)

        # Load textures for falling
        self.fall = []
        self.add_animation(main_path, fall, "fall", self.fall)

        self.anim_texture = self.idle_texture_pair

    def add_animation(self, main_path: str, file_name: str, key: str, textures: list):
        for i in range(anim_dict[key]["max_frame"]):
            texture = load_texture_pair(f"{main_path}{file_name}{i}.png")
            textures.append(texture)

        self.anim_texture_map[key] = textures

    def change_animation(self, desired: str):
        if self.curr_anim != desired:
            self.curr_anim = desired
            self.cur_texture = 0
            self.anim_texture = self.anim_texture_map[desired]

    def notify_keypress(self, pressed_key):
        if pressed_key == keymap[self.keymap_conf]["up"]:
            if self.physics_engine.is_on_ladder():
                self.change_y = PLAYER_MOVEMENT_SPEED
            elif self.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                arcade.play_sound(self.jump_sound)
        elif pressed_key == keymap[self.keymap_conf]["left"]:
            self.change_x = -PLAYER_MOVEMENT_SPEED
        elif pressed_key == keymap[self.keymap_conf]["right"]:
            self.change_x = PLAYER_MOVEMENT_SPEED

    def notify_keyrelease(self, released_key):
        if released_key == keymap[self.keymap_conf]["up"] and self.physics_engine.is_on_ladder():
            self.change_y = 0
        if released_key == keymap[self.keymap_conf]["left"]:
            self.change_x = 0
        elif released_key == keymap[self.keymap_conf]["right"]:
            self.change_x = 0

    def can_jump(self):
        return self.physics_engine.can_jump()

    def update_character(self):
        self.update_animation()
        self.update_physics()

    def update_physics(self):
        self.physics_engine.update()

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        direction = self.character_face_direction

        # Change current animation to desired one
        if self.change_x == 0 and self.change_y == 0:
            self.change_animation("idle")
        elif self.change_x != 0 and self.change_y == 0:
            self.change_animation("run")
        elif self.change_y > 0 and self.physics_engine.jumps_since_ground == 1 and not self.physics_engine.is_on_ladder():
            self.change_animation("jump")
        elif self.change_y > 0 and self.physics_engine.jumps_since_ground == 2 and not self.physics_engine.is_on_ladder():
            self.change_animation("djump")
        elif self.change_y < 0:
            self.change_animation("fall")

        # Rationale: we update an image frame every UPDATES_PER_FRAME times the update_animation is called
        #            the lower the UPDATES_PER_FRAME value, the faster the animation
        frame = self.cur_texture // UPDATES_PER_FRAME
        self.cur_texture += 1

        if self.cur_texture > (anim_dict[self.curr_anim]["max_frame"] - 1) * UPDATES_PER_FRAME:
            self.cur_texture = 0

        self.texture = self.anim_texture[frame][direction]


class PlayerCharacterJoy(PlayerCharacter):
    def __init__(self, character: str, keymap_conf: str, center_x, center_y, platforms, gravity_constant, ladders,
                 walls):
        # Set up parent class
        super().__init__(character, keymap_conf, center_x, center_y, platforms, gravity_constant, ladders, walls)

        joysticks = arcade.get_joysticks()

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

    def update_character(self):
        if self.joystick:
            # x-axis
            self.change_x = self.joystick.x * PLAYER_MOVEMENT_SPEED
            # Set a "dead zone" to prevent drive from a centered joystick
            if abs(self.change_x) < 0.5:
                self.change_x = 0

        self.update_animation()
        self.update_physics()

    def on_joybutton_press(self, _joystick, button):
        """ Handle button-down event for the joystick """
        if button == 0:
            if self.physics_engine.is_on_ladder():
                self.change_y = PLAYER_MOVEMENT_SPEED
            elif self.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                arcade.play_sound(self.jump_sound)

    def on_joybutton_release(self, _joystick, button):
        if button == 0 and self.physics_engine.is_on_ladder():
            self.change_y = 0

    def on_joyhat_motion(self, _joystick, hat_x, hat_y):
        return

    def notify_keypress(self, pressed_key):
        return

    def notify_keyrelease(self, released_key):
        return

