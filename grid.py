class TileGrid:
    
    def __init__(self, size):
        self._size = size
        self._tiles = {}
    
    @property
    def size(self):
        return self._size
    
    def place_tile(self, position, tile):
        self._valid_position(position)
        self._tiles[position] = tile
        
    def get_tile(self, position):
        self._valid_position(position)
        return self._tiles[position]
    
    def swap_tiles(self, a_position, b_position):
        tile_a = self.get_tile(a_position)
        tile_b = self.get_tile(b_position)
        
        self._tiles[a_position], self._tiles[b_position] = tile_b, tile_a
        tile_a.current_position = b_position
        tile_b.current_position = a_position
        
    def all_tiles(self):
        return list(self._tiles.values())
    
    def all_position(self):
        return [
            (row, col)
            for row in range (self._size)
            for col in range (self._size)
        ]
    
    def all_positions(self):
        return self.all_position()
    
    def solved(self):
        return all(tile.correct() for tile in self.all_tiles())
    
    def incorrect_count(self):
        return sum(1 for tile in self.all_tiles() if not tile.correct())
    
    def reindex_in_home_position(self):
        self._tiles = {tile.home_position: tile for tile in self.all_tiles()}
    
    def _valid_position(self, position):
        row, col = position
        if not (0 <= row < self._size and 00 <= col < self._size):
            raise ValueError(
                f'Position {position} is out of bounds for a {self._size}x{self._size} grid'
            )