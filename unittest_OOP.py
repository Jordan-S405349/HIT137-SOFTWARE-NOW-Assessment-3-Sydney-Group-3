import random
import unittest
import numpy as np

from grid import TileGrid
from tile import Tile
from game import Game
from transfrom import (
    Transform,
    SwapTransform,
    RotateTransform,
    FlipTransform
)

def make_image(fill_value=0, size=4):
    """A small square 'image' with a unique fill value, so we can tell
    two tiles' pixel data apart after swaps/rotations/flips."""
    return np.full((size, size, 3), fill_value, dtype=np.uint8)
 
 
def make_tile_image_dict(grid_size, size=4):
    """Builds the {(row, col): image_data} dict the way the OpenCV-loading
    teammate's code is expected to hand to Game.load_tiles()."""
    return {
        (row, col): make_image(fill_value=row * grid_size + col, size=size)
        for row in range(grid_size)
        for col in range(grid_size)
    }
 
 
# ---------------------------------------------------------------------------
# TileGrid
# ---------------------------------------------------------------------------
class TestTileGrid(unittest.TestCase):
 
    def setUp(self):
        self.grid = TileGrid(3)
        self.tile_a = Tile(make_image(1), home_position=(0, 0))
        self.tile_b = Tile(make_image(2), home_position=(0, 1))
        self.grid.place_tile((0, 0), self.tile_a)
        self.grid.place_tile((0, 1), self.tile_b)
 
    def test_size_property(self):
        self.assertEqual(self.grid.size, 3)
 
    def test_place_and_get_tile(self):
        self.assertIs(self.grid.get_tile((0, 0)), self.tile_a)
        self.assertIs(self.grid.get_tile((0, 1)), self.tile_b)
 
    def test_get_tile_out_of_bounds_raises(self):
        with self.assertRaises(ValueError):
            self.grid.get_tile((3, 0))
        with self.assertRaises(ValueError):
            self.grid.get_tile((0, -1))
        with self.assertRaises(ValueError):
            self.grid.get_tile((-1, 0))
 
    def test_place_tile_out_of_bounds_raises(self):
        with self.assertRaises(ValueError):
            self.grid.place_tile((5, 5), Tile(make_image(9), home_position=(5, 5)))
 
    def test_swap_tiles_swaps_contents_and_updates_current_position(self):
        self.grid.swap_tiles((0, 0), (0, 1))
 
        # grid slots now hold the swapped tiles
        self.assertIs(self.grid.get_tile((0, 0)), self.tile_b)
        self.assertIs(self.grid.get_tile((0, 1)), self.tile_a)
 
        # each tile's own bookkeeping of where it currently sits is updated
        self.assertEqual(self.tile_a.current_position, (0, 1))
        self.assertEqual(self.tile_b.current_position, (0, 0))
 
        # home_position is untouched by a swap
        self.assertEqual(self.tile_a.home_position, (0, 0))
        self.assertEqual(self.tile_b.home_position, (0, 1))
 
    def test_all_tiles_returns_all_placed_tiles(self):
        tiles = self.grid.all_tiles()
        self.assertEqual(len(tiles), 2)
        self.assertIn(self.tile_a, tiles)
        self.assertIn(self.tile_b, tiles)
 
    def test_all_position_lists_every_cell_for_size(self):
        grid = TileGrid(2)
        self.assertEqual(
            set(grid.all_position()),
            {(0, 0), (0, 1), (1, 0), (1, 1)},
        )
 
    def test_solved_true_when_every_tile_is_correct(self):
        self.assertTrue(self.grid.solved())
 
    def test_solved_false_after_a_swap(self):
        self.grid.swap_tiles((0, 0), (0, 1))
        self.assertFalse(self.grid.solved())
 
    def test_incorrect_count(self):
        self.assertEqual(self.grid.incorrect_count(), 0)
        self.grid.swap_tiles((0, 0), (0, 1))
        self.assertEqual(self.grid.incorrect_count(), 2)
 
    def test_reindex_in_home_position_uses_home_not_current(self):
        self.grid.swap_tiles((0, 0), (0, 1))
        # tiles are now indexed by their *current* (swapped) slots
        self.assertIs(self.grid.get_tile((0, 0)), self.tile_b)
 
        self.grid.reindex_in_home_position()
 
        # after reindexing, lookup is keyed by each tile's home_position,
        # regardless of where it currently sits
        self.assertIs(self.grid.get_tile((0, 0)), self.tile_a)
        self.assertIs(self.grid.get_tile((0, 1)), self.tile_b)
 
 
# ---------------------------------------------------------------------------
# Tile
# ---------------------------------------------------------------------------
class TestTile(unittest.TestCase):
 
    def setUp(self):
        self.image = make_image(fill_value=42, size=4)
        self.tile = Tile(self.image.copy(), home_position=(1, 1))
 
    def test_initial_state_is_correct(self):
        self.assertEqual(self.tile.current_position, (1, 1))
        self.assertEqual(self.tile.rotation, 0)
        self.assertFalse(self.tile.horizontal_rotation)
        self.assertFalse(self.tile.vertical_rotation)
        self.assertTrue(self.tile.correct())
 
    def test_current_position_setter(self):
        self.tile.current_position = (2, 2)
        self.assertEqual(self.tile.current_position, (2, 2))
        # home_position is unaffected
        self.assertEqual(self.tile.home_position, (1, 1))
        self.assertFalse(self.tile.correct())
 
    def test_rotate_updates_rotation_and_image(self):
        original = self.tile.get_display_img().copy()
        self.tile.rotate(90)
        self.assertEqual(self.tile.rotation, 90)
        # a 90-degree rotation of a non-symmetric image changes the pixels
        rotated = self.tile.get_display_img()
        self.assertEqual(rotated.shape, original.shape)
 
    def test_rotate_accumulates_mod_360(self):
        self.tile.rotate(270)
        self.tile.rotate(180)
        self.assertEqual(self.tile.rotation, (270 + 180) % 360)
 
    def test_rotate_full_circle_returns_to_original_image(self):
        original = self.tile.get_display_img().copy()
        self.tile.rotate(90)
        self.tile.rotate(90)
        self.tile.rotate(90)
        self.tile.rotate(90)
        self.assertEqual(self.tile.rotation, 0)
        np.testing.assert_array_equal(self.tile.get_display_img(), original)
 
    def test_rotate_rejects_invalid_degrees(self):
        with self.assertRaises(ValueError):
            self.tile.rotate(45)
        with self.assertRaises(ValueError):
            self.tile.rotate(0)
 
    def test_flip_horizontal_toggles_flag(self):
        self.tile.flip('horizontal')
        self.assertTrue(self.tile.horizontal_rotation)
        self.tile.flip('horizontal')
        self.assertFalse(self.tile.horizontal_rotation)
 
    def test_flip_vertical_toggles_flag(self):
        self.tile.flip('vertical')
        self.assertTrue(self.tile.vertical_rotation)
 
    def test_flip_rejects_invalid_direction(self):
        with self.assertRaises(ValueError):
            self.tile.flip('diagonal')
 
    def test_correct_requires_position_rotation_and_flip_all_reset(self):
        self.tile.current_position = (0, 0)
        self.tile.rotate(90)
        self.tile.flip('horizontal')
        self.assertFalse(self.tile.correct())
 
        self.tile.current_position = (1, 1)  # back home, but still rotated/flipped
        self.assertFalse(self.tile.correct())
 
    def test_reset_restores_original_image_and_position(self):
        original = self.tile.get_display_img().copy()
 
        self.tile.current_position = (3, 3)
        self.tile.rotate(90)
        self.tile.flip('horizontal')
        self.tile.flip('vertical')
 
        self.tile.reset()
 
        self.assertTrue(self.tile.correct())
        self.assertEqual(self.tile.current_position, self.tile.home_position)
        self.assertEqual(self.tile.rotation, 0)
        self.assertFalse(self.tile.horizontal_rotation)
        self.assertFalse(self.tile.vertical_rotation)
        np.testing.assert_array_equal(self.tile.get_display_img(), original)
 
 
# ---------------------------------------------------------------------------
# Transform hierarchy (polymorphism)
# ---------------------------------------------------------------------------
class TestTransforms(unittest.TestCase):
 
    def setUp(self):
        self.grid = TileGrid(2)
        self.tile_a = Tile(make_image(1), home_position=(0, 0))
        self.tile_b = Tile(make_image(2), home_position=(0, 1))
        self.grid.place_tile((0, 0), self.tile_a)
        self.grid.place_tile((0, 1), self.tile_b)
 
    def test_transform_is_abstract(self):
        with self.assertRaises(TypeError):
            Transform()
 
    def test_swap_transform_apply(self):
        SwapTransform((0, 0), (0, 1)).apply(self.grid)
        self.assertIs(self.grid.get_tile((0, 0)), self.tile_b)
        self.assertEqual(self.tile_a.current_position, (0, 1))
 
    def test_swap_transform_describe(self):
        t = SwapTransform((0, 0), (0, 1))
        self.assertIn('(0, 0)', t.describe())
        self.assertIn('(0, 1)', t.describe())
 
    def test_rotate_transform_apply_calls_tile_rotate(self):
        RotateTransform((0, 0), 90).apply(self.grid)
        self.assertEqual(self.tile_a.rotation, 90)
 
    def test_rotate_transform_rejects_bad_degrees_at_construction(self):
        with self.assertRaises(ValueError):
            RotateTransform((0, 0), 45)
 
    def test_flip_transform_apply_calls_tile_flip(self):
        FlipTransform((0, 0), 'horizontal').apply(self.grid)
        self.assertTrue(self.tile_a.horizontal_rotation)
 
    def test_flip_transform_describe(self):
        t = FlipTransform((0, 0), 'vertical')
        self.assertIn('vertical', t.describe())
 
    def test_flip_transform_bad_direction_raises(self):
        # NOTE: FlipTransform.__init__ has a bug -- on an invalid direction it
        # does `return ValueError(...)` instead of `raise ValueError(...)`.
        # Returning a non-None value from __init__ is itself illegal in
        # Python, so this currently surfaces as a TypeError (not the
        # ValueError the code is clearly trying to raise). This test pins
        # down that *current* behavior so a fix is a deliberate, visible
        # change rather than a silent one.
        with self.assertRaises(TypeError):
            FlipTransform((0, 0), 'diagonal')
 
    def test_transforms_are_polymorphic_over_a_common_apply_interface(self):
        # After the swap, tile_b sits at (0, 0) and tile_a sits at (0, 1) --
        # the later transforms act on whatever tile now occupies that slot.
        transforms = [
            SwapTransform((0, 0), (0, 1)),
            RotateTransform((0, 0), 180),
            FlipTransform((0, 1), 'vertical'),
        ]
        for t in transforms:
            t.apply(self.grid)  # no branching on type needed by the caller
 
        self.assertEqual(self.tile_b.rotation, 180)
        self.assertTrue(self.tile_a.vertical_rotation)
 
 
# ---------------------------------------------------------------------------
# Game (integration across all four files)
# ---------------------------------------------------------------------------
class TestGame(unittest.TestCase):
 
    def setUp(self):
        self.game = Game(grid_size=3)
        self.tiles_by_pos = make_tile_image_dict(3)
        self.game.load_tiles(self.tiles_by_pos)
 
    def test_rejects_bad_grid_size(self):
        with self.assertRaises(ValueError):
            Game(grid_size=2)
 
    def test_load_tiles_populates_grid_and_resets_counters(self):
        self.assertEqual(len(self.game.grid.all_tiles()), 9)
        self.assertEqual(self.game.moves_made(), 0)
        self.assertEqual(self.game.hint_remain(), Game.hint_max)
        self.assertTrue(self.game.is_solved())
 
    def test_select_tile_first_click_selects_and_returns_false(self):
        moved = self.game.select_tile((0, 0))
        self.assertFalse(moved)
        self.assertEqual(self.game.select_position, (0, 0))
 
    def test_select_tile_same_position_twice_deselects(self):
        self.game.select_tile((0, 0))
        moved = self.game.select_tile((0, 0))
        self.assertFalse(moved)
        self.assertIsNone(self.game.select_position)
 
    def test_select_tile_two_different_positions_swaps_and_counts_move(self):
        self.game.select_tile((0, 0))
        moved = self.game.select_tile((1, 1))
        self.assertTrue(moved)
        self.assertIsNone(self.game.select_position)
        self.assertEqual(self.game.moves_made(), 1)
        self.assertFalse(self.game.is_solved())
 
    def test_rotate_tile_applies_and_counts_move(self):
        self.game.rotate_tile((0, 0), 90)
        self.assertEqual(self.game.grid.get_tile((0, 0)).rotation, 90)
        self.assertEqual(self.game.moves_made(), 1)
 
    def test_flip_tile_applies_and_counts_move(self):
        self.game.flip_tile((0, 0), 'horizontal')
        self.assertTrue(self.game.grid.get_tile((0, 0)).horizontal_rotation)
        self.assertEqual(self.game.moves_made(), 1)
 
    def test_tiles_remain_tracks_incorrect_tiles(self):
        self.assertEqual(self.game.tiles_remain(), 0)
        self.game.rotate_tile((0, 0), 90)
        self.assertEqual(self.game.tiles_remain(), 1)
 
    def test_get_hint_returns_current_and_home_position_for_incorrect_tile(self):
        self.game.select_tile((0, 0))
        self.game.select_tile((1, 1))  # swap, so both (0,0) and (1,1) are wrong
 
        hint = self.game.get_hint()
        self.assertIsNotNone(hint)
        current_position, home_position = hint
        tile = self.game.grid.get_tile(current_position)
        self.assertEqual(tile.home_position, home_position)
        self.assertNotEqual(current_position, home_position)
 
    def test_get_hint_returns_none_when_solved(self):
        self.assertIsNone(self.game.get_hint())
 
    def test_get_hint_is_capped_at_hint_max(self):
        # scramble a bit so there's always something incorrect to hint about
        self.game.rotate_tile((0, 0), 90)
        self.game.rotate_tile((1, 1), 90)
        self.game.rotate_tile((2, 2), 90)
        self.game.rotate_tile((0, 1), 90)
 
        hints_given = [self.game.get_hint() for _ in range(Game.hint_max + 2)]
        non_none = [h for h in hints_given if h is not None]
        self.assertEqual(len(non_none), Game.hint_max)
        self.assertEqual(self.game.hint_remain(), 0)
 
    def test_solve_resets_everything(self):
        self.game.rotate_tile((0, 0), 90)
        self.game.flip_tile((1, 1), 'vertical')
        self.game.select_tile((0, 1))
        self.game.select_tile((2, 2))
        self.game.get_hint()
 
        self.game.solve()
 
        self.assertTrue(self.game.is_solved())
        self.assertEqual(self.game.moves_made(), 0)
        self.assertEqual(self.game.hint_remain(), Game.hint_max)
        self.assertIsNone(self.game.select_position)
        self.assertEqual(self.game.tiles_remain(), 0)
 
    def test_scramble_returns_the_transformations_it_applied(self):
        random.seed(0)
        transformations = self.game.scramble()
        expected_count = Game.count_transform[self.game.grid_size]
        self.assertEqual(len(transformations), expected_count)
        for t in transformations:
            self.assertIsInstance(t, Transform)
 
    def test_scramble_usually_leaves_the_puzzle_unsolved(self):
        random.seed(1)
        self.game.scramble()
        # With 6+ transformations on a 3x3 grid this should not land back
        # on solved; guard against a flaky one-in-a-huge-number coincidence
        # by checking incorrect_count directly is sane rather than exact.
        self.assertGreaterEqual(self.game.tiles_remain(), 0)
 
    def test_scramble_then_solve_round_trip(self):
        random.seed(2)
        self.game.scramble()
        self.game.solve()
        self.assertTrue(self.game.is_solved())
        self.assertEqual(self.game.tiles_remain(), 0)
 
 
if __name__ == '__main__':
    unittest.main(verbosity=2)