"""
image_processor.py

Defines ImageProcessor: every OpenCV operation the game needs.

  - load an image file (JPG, PNG or BMP) safely
  - crop it to a square and resize it to fit the window, keeping the
    aspect ratio and making the side divide evenly by the grid size
  - split it into tiles for Game.load_tiles()
  - reassemble the current board back into one image
  - draw overlays: a faint grid, the selection border, blue hint circles
    and green ticks on correctly placed tiles

The GUI never calls OpenCV directly; it only asks ImageProcessor for
finished images.
"""

import os

import cv2
import numpy as np


class ImageLoadError(Exception):
    """Raised when a file cannot be used as a puzzle image."""


class ImageProcessor:
    """Loads, prepares, splits, reassembles and decorates puzzle images."""

    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

    # Overlay colours (OpenCV uses BGR order)
    GRID_COLOUR = (255, 255, 255)
    GRID_OPACITY = 0.35                # faint grid lines
    SELECT_COLOUR = (0, 215, 255)      # amber
    HINT_COLOUR = (255, 0, 0)          # blue
    TICK_COLOUR = (0, 200, 0)          # green

    # ----- loading and preparing -------------------------------------------

    def load(self, path):
        """Read an image file and return it as a BGR array.

        Uses np.fromfile + cv2.imdecode instead of cv2.imread so that
        paths with non-English characters work on Windows.
        """
        if not path or not os.path.isfile(path):
            raise ImageLoadError('The selected file does not exist.')

        extension = os.path.splitext(path)[1].lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ImageLoadError(
                f'"{os.path.basename(path)}" is not a supported image.\n'
                'Please choose a JPG, PNG or BMP file.'
            )

        try:
            data = np.fromfile(path, dtype=np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)   # also drops any alpha channel
        except (OSError, cv2.error) as error:
            raise ImageLoadError(f'Could not read the file:\n{error}') from error

        if image is None:
            raise ImageLoadError(
                f'"{os.path.basename(path)}" could not be opened as an image.\n'
                'The file may be damaged or not really an image.'
            )
        return image

    def prepare(self, image, max_side, grid_size):
        """Centre-crop to a square, then resize to fit `max_side`.

        Tiles must be square so a rotated tile still fits its slot, so the
        image is cropped to its central square first (no stretching, so the
        aspect ratio is kept). The final side is the largest multiple of
        grid_size that fits, so every tile has exactly the same size.
        """
        height, width = image.shape[:2]
        side = min(height, width)
        top = (height - side) // 2
        left = (width - side) // 2
        square = image[top:top + side, left:left + side]

        target = (max_side // grid_size) * grid_size
        if target < grid_size:
            raise ValueError('Display area is too small for this grid size')

        interpolation = cv2.INTER_AREA if side > target else cv2.INTER_LINEAR
        return cv2.resize(square, (target, target), interpolation=interpolation)

    def split(self, image, grid_size):
        """Cut a prepared square image into {(row, col): tile_image}."""
        tile_side = image.shape[0] // grid_size
        return {
            (row, col): image[row * tile_side:(row + 1) * tile_side,
                              col * tile_side:(col + 1) * tile_side].copy()
            for row in range(grid_size)
            for col in range(grid_size)
        }

    def assemble(self, grid):
        """Rebuild one image from the tiles currently on a TileGrid."""
        rows = []
        for row in range(grid.size):
            tiles = [grid.get_tile((row, col)).get_display_img() for col in range(grid.size)]
            rows.append(np.hstack(tiles))
        return np.vstack(rows)

    # ----- overlays --------------------------------------------------------

    def render_puzzle(self, grid, selected=None, hint_position=None, show_ticks=True):
        """Return the scrambled board with all gameplay overlays drawn."""
        image = self.assemble(grid)
        tile_side = image.shape[0] // grid.size

        if show_ticks:
            for position in grid.all_positions():
                if grid.get_tile(position).correct():
                    self._draw_tick(image, position, tile_side)

        self._draw_grid_lines(image, grid.size)

        if hint_position is not None:
            self._draw_hint_circle(image, hint_position, tile_side)
        if selected is not None:
            self._draw_box(image, selected, tile_side, self.SELECT_COLOUR)
        return image

    def render_original(self, image, grid_size, hint_position=None):
        """Return the reference image with an optional blue hint circle."""
        result = image.copy()
        if hint_position is not None:
            self._draw_hint_circle(result, hint_position, result.shape[0] // grid_size)
        return result

    def _line_width(self, tile_side):
        return max(2, tile_side // 30)

    def _draw_grid_lines(self, image, grid_size):
        """Blend thin grid lines into the image so tile edges show faintly."""
        side = image.shape[0]
        tile_side = side // grid_size
        lines = image.copy()
        for i in range(1, grid_size):
            offset = i * tile_side
            cv2.line(lines, (offset, 0), (offset, side - 1), self.GRID_COLOUR, 1)
            cv2.line(lines, (0, offset), (side - 1, offset), self.GRID_COLOUR, 1)
        cv2.addWeighted(lines, self.GRID_OPACITY, image, 1 - self.GRID_OPACITY, 0, dst=image)

    def _draw_hint_circle(self, image, position, tile_side):
        """Draw a blue circle in the middle of a tile."""
        row, col = position
        centre = (col * tile_side + tile_side // 2, row * tile_side + tile_side // 2)
        radius = int(tile_side * 0.38)
        width = self._line_width(tile_side) + 1
        cv2.circle(image, centre, radius, (255, 255, 255), width + 2, cv2.LINE_AA)
        cv2.circle(image, centre, radius, self.HINT_COLOUR, width, cv2.LINE_AA)

    def _draw_box(self, image, position, tile_side, colour):
        row, col = position
        width = self._line_width(tile_side)
        inset = width // 2
        top_left = (col * tile_side + inset, row * tile_side + inset)
        bottom_right = ((col + 1) * tile_side - 1 - inset, (row + 1) * tile_side - 1 - inset)
        cv2.rectangle(image, top_left, bottom_right, colour, width)

    def _draw_tick(self, image, position, tile_side):
        """Draw a small green tick in the tile's top-right corner."""
        row, col = position
        size = max(10, tile_side // 5)
        x = (col + 1) * tile_side - size - 4
        y = row * tile_side + 4
        points = np.array([
            (x + size * 0.15, y + size * 0.55),
            (x + size * 0.40, y + size * 0.80),
            (x + size * 0.85, y + size * 0.20),
        ], dtype=np.int32)
        cv2.polylines(image, [points], False, (255, 255, 255), self._line_width(tile_side) + 2, cv2.LINE_AA)
        cv2.polylines(image, [points], False, self.TICK_COLOUR, self._line_width(tile_side), cv2.LINE_AA)