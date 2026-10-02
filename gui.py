"""
gui.py

Defines PuzzleApp: the Tkinter window.

The GUI only handles layout, input and display. All game rules live in
Game and all OpenCV work lives in ImageProcessor, so this class just
turns clicks into Game calls and shows the images ImageProcessor draws.

Controls
  Left-click    select a tile, then click another tile to swap them
  Right-click   rotate a tile 90 degrees clockwise (Ctrl+click on macOS)
  Shift+click   flip a tile horizontally
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from game import Game, DIFFICULTIES
from image_processor import ImageProcessor, ImageLoadError


class PuzzleApp:
    """Main window: side-by-side images, controls and a status bar."""

    GRID_CHOICES = {'3 x 3': 3, '4 x 4': 4, '5 x 5': 5}
    FILE_TYPES = [('Image files', '*.jpg *.jpeg *.png *.bmp'),
                  ('JPEG', '*.jpg *.jpeg'), ('PNG', '*.png'), ('Bitmap', '*.bmp')]
    BACKGROUND = '#1e1e24'
    PANEL = '#2a2a33'
    TEXT = '#f0f0f0'

    def __init__(self, root):
        self._root = root
        self._processor = ImageProcessor()
        self._game = None
        self._source_image = None      # image as loaded from disk
        self._prepared_image = None    # cropped/resized square shown on screen
        self._hint = None              # (current_position, home_position)
        self._photos = {}              # keep PhotoImage references alive
        self._timer_job = None

        screen_limit = root.winfo_screenheight() - 260
        self._canvas_size = max(300, min(480, screen_limit))

        self._grid_var = tk.StringVar(value='3 x 3')
        self._difficulty_var = tk.StringVar(value='Medium')
        self._status_vars = {name: tk.StringVar(value='-') for name in
                             ('moves', 'tiles', 'hints', 'score', 'time')}
        self._message_var = tk.StringVar(value='Load an image to start.')

        self._build_window()
        self._bind_mouse()
        root.report_callback_exception = self._show_unexpected_error

    # ----- layout ----------------------------------------------------------

    def _build_window(self):
        root = self._root
        root.title('Image Tile Puzzle')
        root.configure(bg=self.BACKGROUND)
        root.resizable(False, False)

        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TButton', padding=(10, 5))

        controls = tk.Frame(root, bg=self.BACKGROUND, pady=10)
        controls.pack(fill='x', padx=16)

        ttk.Button(controls, text='Load Image', command=self.load_image).pack(side='left')
        self._add_label(controls, 'Grid').pack(side='left', padx=(16, 4))
        grid_box = ttk.Combobox(controls, textvariable=self._grid_var, width=6,
                                values=list(self.GRID_CHOICES), state='readonly')
        grid_box.pack(side='left')
        grid_box.bind('<<ComboboxSelected>>', lambda event: self._settings_changed())

        self._add_label(controls, 'Difficulty').pack(side='left', padx=(16, 4))
        level_box = ttk.Combobox(controls, textvariable=self._difficulty_var, width=8,
                                 values=list(DIFFICULTIES), state='readonly')
        level_box.pack(side='left')
        level_box.bind('<<ComboboxSelected>>', lambda event: self._settings_changed())

        self._solve_button = ttk.Button(controls, text='Solve', command=self.solve, state='disabled')
        self._solve_button.pack(side='right')
        self._hint_button = ttk.Button(controls, text='Hint', command=self.show_hint, state='disabled')
        self._hint_button.pack(side='right', padx=6)
        ttk.Button(controls, text='New Round', command=self.new_round).pack(side='right')

        boards = tk.Frame(root, bg=self.BACKGROUND)
        boards.pack(padx=16)
        self._original_canvas = self._add_board(boards, 'Original', column=0)
        self._puzzle_canvas = self._add_board(boards, 'Puzzle', column=1)

        status = tk.Frame(root, bg=self.PANEL, padx=12, pady=8)
        status.pack(fill='x', padx=16, pady=(10, 4))
        for title, key in [('Moves', 'moves'), ('Tiles left', 'tiles'), ('Hints left', 'hints'),
                           ('Score', 'score'), ('Time', 'time')]:
            cell = tk.Frame(status, bg=self.PANEL)
            cell.pack(side='left', expand=True)
            tk.Label(cell, text=title, bg=self.PANEL, fg='#a0a0b0', font=('Segoe UI', 9)).pack()
            tk.Label(cell, textvariable=self._status_vars[key], bg=self.PANEL, fg=self.TEXT,
                     font=('Segoe UI', 14, 'bold')).pack()

        tk.Label(root, textvariable=self._message_var, bg=self.BACKGROUND, fg=self.TEXT,
                 font=('Segoe UI', 10)).pack(pady=(4, 2))
        rotate_key = 'Right-click (or Ctrl+click)' if sys.platform == 'darwin' else 'Right-click'
        tk.Label(root, text=f'Left-click: select / swap    {rotate_key}: rotate    Shift+click: flip',
                 bg=self.BACKGROUND, fg='#a0a0b0', font=('Segoe UI', 9)).pack(pady=(0, 10))

    def _add_label(self, parent, text):
        return tk.Label(parent, text=text, bg=self.BACKGROUND, fg=self.TEXT)

    def _add_board(self, parent, title, column):
        frame = tk.Frame(parent, bg=self.BACKGROUND)
        frame.grid(row=0, column=column, padx=8)
        tk.Label(frame, text=title, bg=self.BACKGROUND, fg=self.TEXT,
                 font=('Segoe UI', 11, 'bold')).pack(pady=(0, 4))
        canvas = tk.Canvas(frame, width=self._canvas_size, height=self._canvas_size,
                           bg=self.PANEL, highlightthickness=0)
        canvas.pack()
        return canvas

    def _bind_mouse(self):
        canvas = self._puzzle_canvas
        canvas.bind('<Button-1>', self._on_left_click)
        canvas.bind('<Shift-Button-1>', self._on_shift_click)
        if sys.platform == 'darwin':
            canvas.bind('<Button-2>', self._on_right_click)
            canvas.bind('<Control-Button-1>', self._on_right_click)
        else:
            canvas.bind('<Button-3>', self._on_right_click)

    # ----- loading and starting rounds -------------------------------------

    def load_image(self):
        """Ask for an image file and start a new round with it."""
        path = filedialog.askopenfilename(title='Choose an image', filetypes=self.FILE_TYPES)
        if not path:
            return  # dialog cancelled: keep the current game as it is
        try:
            image = self._processor.load(path)
        except ImageLoadError as error:
            messagebox.showerror('Cannot load image', str(error))
            return
        self._source_image = image
        self.new_round()

    def new_round(self):
        """Start a fresh round with the current image and settings."""
        if self._source_image is None:
            messagebox.showinfo('No image', 'Please load an image first.')
            return

        grid_size = self.GRID_CHOICES[self._grid_var.get()]
        self._prepared_image = self._processor.prepare(self._source_image, self._canvas_size, grid_size)
        self._game = Game(grid_size, self._difficulty_var.get())
        self._game.load_tiles(self._processor.split(self._prepared_image, grid_size))
        self._game.scramble()
        self._hint = None
        self._message_var.set('Restore the picture!')
        self._refresh()
        self._restart_timer()

    def _settings_changed(self):
        """Grid size or difficulty changed: start again if a game is running."""
        if self._source_image is not None:
            self.new_round()

    # ----- mouse input -----------------------------------------------------

    def _tile_at(self, event):
        """Convert a click to a (row, col), or None if it is off the image."""
        if self._game is None:
            return None
        side = self._prepared_image.shape[0]
        offset = (self._canvas_size - side) // 2
        x, y = event.x - offset, event.y - offset
        if not (0 <= x < side and 0 <= y < side):
            return None
        tile_side = side // self._game.grid_size
        return y // tile_side, x // tile_side

    def _on_left_click(self, event):
        position = self._tile_at(event)
        if position is None or self._game.is_locked():
            return
        if self._game.select_tile(position):
            self._hint = None   # a swap is a move, so the hint circle goes
        self._after_action()

    def _on_right_click(self, event):
        position = self._tile_at(event)
        if position is None or self._game.is_locked():
            return
        self._hint = None
        self._game.rotate_tile(position, 90)
        self._after_action()

    def _on_shift_click(self, event):
        position = self._tile_at(event)
        if position is None or self._game.is_locked():
            return 'break'
        self._hint = None
        self._game.flip_tile(position, 'horizontal')
        self._after_action()
        return 'break'   # stop the plain left-click binding also firing

    def _after_action(self):
        self._refresh()
        if self._game.state == Game.WON:
            self._stop_timer()
            self._message_var.set('Solved! Load a new image or press New Round.')
            messagebox.showinfo(
                'Puzzle complete',
                f'Well done! You restored the picture in {self._game.moves_made()} moves.\n'
                f'Final score: {self._game.score()}'
            )

    # ----- buttons ---------------------------------------------------------

    def show_hint(self):
        """Circle one wrong tile on the puzzle and its home on the original."""
        if self._game is None or self._game.is_locked():
            return
        hint = self._game.get_hint()
        if hint is None:
            return
        self._hint = hint
        current, home = hint
        where = f'row {current[0] + 1}, column {current[1] + 1}'
        if current == home:
            self._message_var.set(f'Hint: the tile at {where} is in the right place but needs turning.')
        else:
            self._message_var.set(f'Hint: the tile at {where} belongs at '
                                  f'row {home[0] + 1}, column {home[1] + 1}.')
        self._refresh()

    def solve(self):
        """Reveal the solution after asking the player to confirm."""
        if self._game is None or self._game.is_locked():
            return
        if not messagebox.askyesno('Solve puzzle', 'Show the solution? Moves and score will be cleared.'):
            return
        self._game.solve()
        self._hint = None
        self._stop_timer()
        self._message_var.set('Solved automatically. Press New Round to try again.')
        self._refresh()

    # ----- timer -----------------------------------------------------------

    def _restart_timer(self):
        self._stop_timer()
        self._tick()

    def _stop_timer(self):
        if self._timer_job is not None:
            self._root.after_cancel(self._timer_job)
            self._timer_job = None

    def _tick(self):
        self._update_status()
        if self._game.check_time():
            self._timer_job = None
            self._hint = None
            self._message_var.set("Time's up! Press New Round to try again.")
            self._refresh()
            messagebox.showwarning("Time's up", 'You ran out of time. The board is now locked.')
            return
        self._timer_job = self._root.after(1000, self._tick)

    # ----- drawing ---------------------------------------------------------

    def _refresh(self):
        """Redraw both images and the status bar from the current game state."""
        current_hint, home_hint = self._hint if self._hint else (None, None)
        original = self._processor.render_original(self._prepared_image, self._game.grid_size, home_hint)
        puzzle = self._processor.render_puzzle(self._game.grid, self._game.selected_position, current_hint)
        self._show(self._original_canvas, original, 'original')
        self._show(self._puzzle_canvas, puzzle, 'puzzle')
        self._update_status()
        self._update_buttons()

    def _update_buttons(self):
        """Hint is disabled once 3 hints are used; both are disabled when the round ends."""
        playing = self._game is not None and not self._game.is_locked()
        hint_ok = playing and self._game.hints_remaining() > 0
        self._hint_button.configure(state='normal' if hint_ok else 'disabled')
        self._solve_button.configure(state='normal' if playing else 'disabled')

    def _show(self, canvas, bgr_image, key):
        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(Image.fromarray(rgb))
        self._photos[key] = photo   # without this reference Tk shows a blank canvas
        canvas.delete('all')
        centre = self._canvas_size // 2
        canvas.create_image(centre, centre, image=photo, anchor='center')

    def _update_status(self):
        game = self._game
        seconds = game.time_left()
        self._status_vars['moves'].set(str(game.moves_made()))
        self._status_vars['tiles'].set(str(game.tiles_remaining()))
        self._status_vars['hints'].set(str(game.hints_remaining()))
        self._status_vars['score'].set(str(game.score()))
        self._status_vars['time'].set(f'{seconds // 60}:{seconds % 60:02d}')

    # ----- errors ----------------------------------------------------------

    def _show_unexpected_error(self, exc_type, exc_value, exc_traceback):
        """Show any unexpected error in a message box instead of crashing."""
        messagebox.showerror('Unexpected error', f'{exc_type.__name__}: {exc_value}')


def main():
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()