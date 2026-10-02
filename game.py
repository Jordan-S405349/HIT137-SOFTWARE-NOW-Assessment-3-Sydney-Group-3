"""
game.py
 
Defines Game: the top-level class that owns a TileGrid, tracks moves
and hints, and generates/applies the random scrambling transformations.
 
This is the class the other two members' code plugs into:
  - Whoever writes the OpenCV image loading/splitting calls load_tiles()
    once they have split an image into a dict of (row, col) -> pixel data.
  - Whoever writes the Tkinter GUI calls select_tile(), rotate_tile(),
    flip_tile(), get_hint(), solve(), is_solved(), moves_made(),
    tiles_remain(), and hints_remain() to drive the interface,
    without needing to know anything about how tiles or transformations
    work internally.
"""

import random
import time

from tile import Tile
from grid import TileGrid
from transfrom import (
    Transform,
    SwapTransform,
    RotateTransform,
    FlipTransform
)

DIFFICULTIES = {
    'Easy': 300,
    'Medium': 180,
    'Hard': 90
}

class Game:
    
    hint_max = 3
    count_transform = {3: 6, 4: 12, 5:20}
    
    PLAYING = 'playing'
    WON = 'won'
    TIME_OUT = 'time_out'
    def __init__(self, grid_size=3, difficulty='Medium'):
        if grid_size not in self.count_transform:
            raise ValueError('Grid_size mus be 3, 4 or 5')
        if difficulty not in DIFFICULTIES:
            raise ValueError(f'Difficulty must be one of {list(DIFFICULTIES)}, got {difficulty!r}')
        
        self._grid_size  = grid_size
        self._grid = TileGrid(grid_size)
        self._moves = 0
        self._used_hint = 0
        self._select_position = None
        
        self._difficulty = difficulty
        self._time_limit = DIFFICULTIES[difficulty]
        self._start_time = None
        self._state = self.PLAYING
    
    """ Caleed per loaded image once"""
    
    def load_tiles(self, tile_image):
        for position, image_data in tile_image.items():
            self._grid.place_tile(position, Tile(image_data, home_position=position))
            
        self._moves = 0
        self._used_hint = 0
        self._select_position = None
        self._state = self.PLAYING
        self._start_time = time.time()
        
    def scramble(self):
        transform_count = self.count_transform[self._grid_size]
        transformation = self._generate_random_transform(transform_count)
        
        for transformations in transformation:
            transformations.apply(self._grid)
        
        return transformation
    
    def _generate_random_transform(self, count):
        
        transformations = []
        all_positions =  self._grid.all_position()
        used_in_swap = set()
        
        for _ in range(count):
            kind = random.choice(['swap', 'rotate', 'flip'])
            
            if kind == 'swap':
                available = [p for p in all_positions if p not in used_in_swap]
                if len(available) < 2:
                    kind = 'rotate'
                else:
                    a_position, b_position = random.sample(available, 2)
                    used_in_swap.add(a_position)
                    used_in_swap.add(b_position)
                    transformations.append(SwapTransform(a_position, b_position))
                    continue
                
            if kind == 'rotate':
                position = random.choice(all_positions)
                degrees = random.choice([90, 180, 270])
                transformations.append(RotateTransform(position, degrees))
                continue
                
            position = random.choice(all_positions)
            direction = random.choice(['horizontal', 'vertical'])
            transformations.append(FlipTransform(position, direction))
        
        return transformations

    """ Player actions that are called by the GUI that respons to click"""

    def select_tile(self, position):
        
        if self._select_position is None:
            self._select_position = position
            return False
        
        if self._select_position == position:
            self._select_position = None
            return False
        
        self.apply_transform(SwapTransform(self._select_position, position))
        self._select_position = None
        return True

    def rotate_tile(self, position, degrees=90):
        self.apply_transform(RotateTransform(position, degrees))
        
    def flip_tile(self, position, direction='horizontal'):
        self.apply_transform(FlipTransform(position, direction))

    def apply_transform(self, transform):
        transform.apply(self._grid)
        self._moves += 1
        if self._grid.solved():
            self._state = self.WON

    @property
    def select_position(self):
        return self._select_position
    
    @property
    def selected_position(self):
        return self._select_position

    """ Hints """
    
    def get_hint(self):
        
        if self._used_hint >= self.hint_max:
            return None
        
        incorrect_tiles = [tile for tile in self._grid.all_tiles() if not tile.correct()]
        if not incorrect_tiles:
            return None
        
        self._used_hint += 1
        tile = random.choice(incorrect_tiles)
        return tile.current_position, tile.home_position
    
    def solve(self):
        
        for tile in self._grid.all_tiles():
            tile.reset()
        
        self._grid.reindex_in_home_position()
        self._moves = 0
        self._used_hint = 0
        self._select_position = None
        self._state = self.WON
        
    """ Status is called by GUI to update the on screen counters"""
    
    def is_solved(self):
        return self._grid.solved()
    
    def moves_made(self):
        return self._moves
    
    def tiles_remain(self):
        return self._grid.incorrect_count()
    
    def tiles_remaining(self):
        return self.tiles_remain
    
    def hint_remain(self):
        return self.hint_max - self._used_hint
    
    def hint_remaining(self):
        return self.hint_remain
    
    @property
    def grid(self):
        return self._grid
    
    @property
    def grid_size(self):
        return self._grid_size
    
    @property
    def state(self):
        return self._state
    
    def is_locked(self):
        return self._state != self.PLAYING
    
    def time_left(self):
        if self._start_time is None:
            return self._time_limit
        elapsed = time.time() - self._start_time
        return max(0, int(self._time_limit - elapsed))
    
    def check_time(self):
        if self._state == self.PLAYING and self.time_left() <= 0:
            self._state = self.TIME_OUT
        return self._state == self.TIME_OUT
    
    def score(self):
        base = 1000
        penalty = (self._moves*5) + (self._used_hint*50)
        time_bonus = self.time_left()*2
        return max(0, base - penalty + time_bonus)