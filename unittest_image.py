"""
Unit tests for ImageProcessor. Run with:  python -m unittest unittest_image
"""

import os
import shutil
import tempfile
import unittest

import cv2
import numpy as np

from game import Game
from image_processor import ImageProcessor, ImageLoadError


def make_photo(height, width):
    """A colourful non-symmetric test image."""
    y, x = np.mgrid[0:height, 0:width]
    return np.dstack([(x * 255 // width), (y * 255 // height), ((x + y) % 256)]).astype(np.uint8)


class TestLoading(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.processor = ImageProcessor()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def _save(self, name, image=None):
        path = os.path.join(self.folder, name)
        ok, data = cv2.imencode(os.path.splitext(name)[1], make_photo(90, 120) if image is None else image)
        data.tofile(path)
        return path

    def test_loads_jpg_png_bmp(self):
        for name in ('photo.jpg', 'photo.jpeg', 'photo.png', 'photo.bmp', 'PHOTO.PNG'):
            image = self.processor.load(self._save(name))
            self.assertEqual(image.shape, (90, 120, 3))

    def test_png_with_transparency_becomes_three_channels(self):
        rgba = np.zeros((20, 20, 4), dtype=np.uint8)
        image = self.processor.load(self._save('alpha.png', rgba))
        self.assertEqual(image.shape, (20, 20, 3))

    def test_non_english_path(self):
        image = self.processor.load(self._save('تصویر.png'))
        self.assertEqual(image.shape[2], 3)

    def test_missing_file(self):
        with self.assertRaises(ImageLoadError):
            self.processor.load(os.path.join(self.folder, 'nope.png'))

    def test_empty_path_from_cancelled_dialog(self):
        with self.assertRaises(ImageLoadError):
            self.processor.load('')

    def test_wrong_extension(self):
        path = os.path.join(self.folder, 'notes.txt')
        with open(path, 'w') as file:
            file.write('hello')
        with self.assertRaises(ImageLoadError):
            self.processor.load(path)

    def test_fake_image_file(self):
        path = os.path.join(self.folder, 'fake.png')
        with open(path, 'w') as file:
            file.write('not really a png')
        with self.assertRaises(ImageLoadError):
            self.processor.load(path)


class TestPrepareSplitAssemble(unittest.TestCase):

    def setUp(self):
        self.processor = ImageProcessor()

    def test_prepare_gives_square_divisible_by_grid(self):
        for shape in [(300, 500), (500, 300), (1000, 1000), (37, 53)]:
            for grid_size in (3, 4, 5):
                result = self.processor.prepare(make_photo(*shape), 500, grid_size)
                self.assertEqual(result.shape[0], result.shape[1])
                self.assertEqual(result.shape[0] % grid_size, 0)
                self.assertLessEqual(result.shape[0], 500)

    def test_prepare_does_not_stretch(self):
        # A wide image keeps its centre: the middle column of the crop is the original centre.
        image = make_photo(100, 300)
        result = self.processor.prepare(image, 99, 3)
        self.assertEqual(result.shape[:2], (99, 99))
        np.testing.assert_allclose(result[50, 50].astype(int), image[50, 150].astype(int), atol=6)

    def test_split_makes_equal_square_tiles(self):
        for grid_size in (3, 4, 5):
            image = self.processor.prepare(make_photo(400, 600), 480, grid_size)
            tiles = self.processor.split(image, grid_size)
            self.assertEqual(len(tiles), grid_size ** 2)
            shapes = {tile.shape for tile in tiles.values()}
            self.assertEqual(len(shapes), 1)
            height, width, _ = shapes.pop()
            self.assertEqual(height, width)

    def test_split_then_assemble_round_trip(self):
        for grid_size in (3, 4, 5):
            image = self.processor.prepare(make_photo(400, 600), 480, grid_size)
            game = Game(grid_size)
            game.load_tiles(self.processor.split(image, grid_size))
            np.testing.assert_array_equal(self.processor.assemble(game.grid), image)

    def test_scramble_changes_image_and_solve_restores_it(self):
        image = self.processor.prepare(make_photo(400, 600), 480, 4)
        game = Game(4)
        game.load_tiles(self.processor.split(image, 4))
        game.scramble()
        self.assertFalse(np.array_equal(self.processor.assemble(game.grid), image))
        game.solve()
        np.testing.assert_array_equal(self.processor.assemble(game.grid), image)


class TestOverlays(unittest.TestCase):

    def setUp(self):
        self.processor = ImageProcessor()
        self.image = self.processor.prepare(make_photo(300, 300), 300, 3)
        self.game = Game(3)
        self.game.load_tiles(self.processor.split(self.image, 3))

    def test_render_keeps_size_and_leaves_tiles_untouched(self):
        rendered = self.processor.render_puzzle(self.game.grid, selected=(0, 0), hint_position=(1, 1))
        self.assertEqual(rendered.shape, self.image.shape)
        # Overlays are drawn on a copy, never on the tiles themselves
        np.testing.assert_array_equal(self.processor.assemble(self.game.grid), self.image)

    def _has_colour(self, image, position, colour):
        """True if any pixel inside the tile at `position` is exactly `colour`."""
        row, col = position
        tile = image[row * 100:(row + 1) * 100, col * 100:(col + 1) * 100]
        return bool(np.all(tile == colour, axis=2).any())

    def test_selection_border_and_hint_circle_are_drawn(self):
        marked = self.processor.render_puzzle(self.game.grid, selected=(0, 0), hint_position=(2, 2),
                                              show_ticks=False)
        self.assertTrue((marked[2, 2] == ImageProcessor.SELECT_COLOUR).all())
        self.assertTrue(self._has_colour(marked, (2, 2), ImageProcessor.HINT_COLOUR))
        self.assertFalse(self._has_colour(marked, (1, 1), ImageProcessor.HINT_COLOUR))

    def test_grid_is_faint(self):
        plain = np.zeros((300, 300, 3), dtype=np.uint8)
        game = Game(3)
        game.load_tiles(self.processor.split(plain, 3))
        rendered = self.processor.render_puzzle(game.grid, show_ticks=False)
        line_value = rendered[150, 100, 0]          # a point on the first vertical line
        self.assertGreater(line_value, 0)           # visible...
        self.assertLess(line_value, 255)            # ...but not solid white

    def test_original_render_marks_hint_with_circle(self):
        rendered = self.processor.render_original(self.image, 3, hint_position=(0, 2))
        self.assertTrue(self._has_colour(rendered, (0, 2), ImageProcessor.HINT_COLOUR))
        np.testing.assert_array_equal(self.processor.render_original(self.image, 3), self.image)


if __name__ == '__main__':
    unittest.main()