import cv2

class Tile:
    rotations = (0, 90, 180, 270)
    direction = ('horizontal', 'vertical')

    rotation_map = {
        90: cv2.ROTATE_90_CLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_COUNTERCLOCKWISE
    }
    
    flip_code = {
        'horizontal': 1,
        'vertical': 0
    }

    def __init__(self, image, home_position):
        self._image = image
        self._home_position = home_position
        
        self._current_position = home_position

        self._rotation = 0
        self._horizontal_rotation = False
        self._vertical_rotation = False

    @property
    def home_position(self):
        return self._home_position

    @property
    def rotation(self):
        return self._rotation

    @property
    def horizontal_rotation(self):
        return self._horizontal_rotation

    @property
    def vertical_rotation(self):
        return self._vertical_rotation
    
    @property
    def current_position(self):
        return self._current_position
    
    @current_position.setter
    def current_position(self, new_position):
        self._current_position = new_position
    
    def rotate(self, degrees=90):
        if degrees not in self.rotations or degrees == 0:
            raise ValueError(f'Rotation must be 90, 180, or 270, got {degrees!r}')
        
        self._image = cv2.rotate(self._image, self.rotation_map[degrees])
        self._rotation = (self._rotation + degrees) % 360
        
    def flip(self, direction='horizontal'):
        if direction not in self.direction:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")
        
        self._image = cv2.flip(self._image, self.flip_code[direction])
        
        if direction == 'horizontal':
            self._horizontal_rotation = not self._horizontal_rotation
        else:
            self._vertical_rotation = not self._vertical_rotation
    
    def reset(self):
        if self._horizontal_rotation:
            self.flip('horizontal')
            
        if self.vertical_rotation:
            self.flip('vertical')
        
        if self._rotation != 0:
            self.rotate(360 - self._rotation)
        
        self._current_position = self._home_position
        
    def correct(self):
        return (
            self._current_position == self._home_position
            and self._rotation == 0
            and not self._horizontal_rotation
            and not self._vertical_rotation
        )
        
    def get_display_img(self):
        return self._image