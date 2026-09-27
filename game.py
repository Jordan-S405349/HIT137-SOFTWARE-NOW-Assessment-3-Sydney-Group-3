import random
from tile import Tile
from grid import TileGrid
from transfrom import (
    Transform,
    SwapTransform,
    RotateTransform,
    FlipTransform
)

class Game:
    
    hint_max = 3
    count_transform = {3: 6, 4: 12, 5:20}
    
    def __init__(self, grid_size=3):
        if grid_size not in self.count_transform:
            raise ValueError('Grid_size mus be 3, 4 or 5')
        
        self._grid_size  = grid_size
        self._grid = TileGrid(grid_size)
        self._moves = 0
        self._used_hint = 0
        self._select_position = None
        
    
    """ Caleed per loaded image once"""
    
    def load_tiles(self, tile_image):
        for position, image_data in tile_image.items():
            self._grid.place_tile(position, Tile(image_data, home_position=position))
            
        self._moves = 0
        self._used_hint = 0
        self._select_position = None
    
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

    @property
    def select_position(self):
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
        
    """ Status is called by GUI to update the on screen counters"""
    
    def is_solved(self):
        return self._grid.solved()
    
    def moves_made(self):
        return self._moves
    
    def tiles_remain(self):
        return self._grid.incorrect_count()
    
    def hint_remain(self):
        return self.hint_max - self._used_hint
    
    @property
    def grid(self):
        return self._grid
    
    @property
    def grid_size(self):
        return self._grid_size