import arcade


# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

UPDATES_PER_FRAME = 5
CHARACTER_SCALING = 1.5


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """

    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self, character: str, center_x, center_y):
        # Set up parent class
        super().__init__()

        self.center_x = center_x
        self.center_y = center_y

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

        # Load textures for idle standing
        self.idle_texture_pair = []
        for i in range(11):
            texture = load_texture_pair(f"{main_path}{idle}{i}.png")
            self.idle_texture_pair.append(texture)

        # Load textures for walking
        self.walk_textures = []
        for i in range(12):
            texture = load_texture_pair(f"{main_path}{run}{i}.png")
            self.walk_textures.append(texture)

        # Load textures for double jumping
        self.double_jump = []
        for i in range(6):
            texture = load_texture_pair(f"{main_path}{double_jump}{i}.png")
            self.double_jump.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        frame = self.cur_texture // UPDATES_PER_FRAME
        self.cur_texture += 1
        
        if self.cur_texture > 5 * UPDATES_PER_FRAME:
            self.cur_texture = 0

        direction = self.character_face_direction

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[frame][self.character_face_direction]
        else:
            # Walking animation
            self.texture = self.walk_textures[frame][direction]




