"""
transformations.py
 
Defines the Transformation class hierarchy: this is the main place this
project demonstrates inheritance and polymorphism on purpose, rather than
just for the sake of having a class hierarchy somewhere.
 
The idea: PuzzleGame can build a list containing a mix of SwapTransform,
RotateTransform, and FlipTransform objects, and apply every one of
them the exact same way:
 
    for transformation in transformations:
        transformation.apply(grid)
 
Game never needs to check "is this a swap or a rotate or a flip?" with
if/elif chains. Each subclass already knows how to apply itself. That's what
polymorphism actually buys you: the calling code stays the same no matter how
many new transformation types get added later.
"""

from abc import ABC, abstractmethod

class Transform(ABC):
    
    @abstractmethod
    def apply(self, grid):
        raise NotImplementedError
    
    @abstractmethod
    def describe(self):
        raise NotImplementedError
    
    
class SwapTransform(Transform):
    
    def __init__(self, a_position, b_position):
        self._a_position = a_position
        self._b_position = b_position
        
    def apply(self, grid):
        grid.swap_tiles(self._a_position, self._b_position)
        
    def describe(self):
        return f'Swap tiles at {self._a_position} and {self._b_position}'


class RotateTransform(Transform):
    
    def __init__(self, position, degrees=90):
        if degrees not in (90, 180, 270):
            raise ValueError('The degrees must be in 90, 180 or 270')
        self._position = position
        self._degrees = degrees
    
    def apply(self, grid):
        tile = grid.get_tile(self._position)
        tile.rotate(self._degrees)
    
    def describe(self):
        return f'The tile got rotated at {self._position} by {self._degrees} degrees'


class FlipTransform(Transform):
    
    def __init__(self, position, direction='horizontal'):
        if direction not in ('horizontal', 'vertical'):
            raise ValueError('The direction must be horizontal or vertical')
        self._position = position
        self._direction = direction
        
    def apply(self, grid):
        tile = grid.get_tile(self._position)
        tile.flip(self._direction)
    
    def describe(self):
        return f'The tile got flipped at {self._position} {self._direction}ly'