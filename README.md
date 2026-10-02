# HIT137-SOFTWARE-NOW-Assessment-3-Sydney-Group-3

## HIT137 Software Now Group Assignment 3

### Group Members

1. Jordan Then Ryan - S405349
2. Areeba Salah Ud Din - S404018
3. Divya Malla - S406481
4. Shraboni Sutradhar - S401805

---

# About This Task

This assignment is a desktop puzzle game developed using Python. A selected image is divided into a scrambled grid of tiles. The player interacts with the tiles to restore the original image. The game supports tile movement, rotation and flipping, while also tracking the player's moves, providing hints, and detecting when the puzzle has been successfully solved.

The project is built around three main areas:

### 1. OOP Design

The project uses object-oriented programming to organise the puzzle components. Classes represent the individual puzzle tiles, the tile grid, and the different operations that can be performed on tiles, including swapping, rotating and flipping.

### 2. Image Processing (OpenCV)

The image-processing component uses **OpenCV and NumPy** to prepare and manage the puzzle images. This includes:

- Loading JPG, JPEG, PNG and BMP image files.
- Validating image files and handling invalid or damaged images.
- Centre-cropping images into a square while maintaining the original aspect ratio.
- Resizing images according to the selected puzzle grid size.
- Ensuring the final image dimensions divide evenly between the puzzle tiles.
- Splitting the prepared image into individual square tiles.
- Reassembling the current puzzle tiles into a complete image.
- Drawing visual overlays such as grid lines, tile selection borders, hint circles and green indicators for correctly positioned tiles.

### 3. Tkinter GUI and Gameplay

The Tkinter component provides the graphical user interface and handles player interaction with the puzzle. It manages the on-screen display, mouse clicks, puzzle controls, move counting, scoring, hints and the solve functionality.

---

# Individual Contributions

## Jordan Then Ryan - S405349

Built the core OOP structure for the puzzle: the Tile class, the TileGrid class, the Transform class hierarchy, and the Game class that ties everything together.

Files contributed:

tile.py: contains the Tile class. Handles a single tile's picture, its home position, its current position, and its rotation and flip state. Includes rotate, flip, reset, and correct methods.

grid.py: contains the TileGrid class. Manages the layout of tiles in the grid, including looking up a tile by position, swapping two tiles, and checking whether the whole grid is solved.

transfrom.py: contains the Transform base class and its three subclasses, SwapTransform, RotateTransform, and FlipTransform. Each one applies a different kind of scramble to the grid through the same shared apply method.

game.py: contains the Game class. Loads tiles into the grid, generates the random scramble when an image is loaded, and handles player actions such as selecting a tile, rotating, flipping, using a hint, and solving the puzzle.

## Shraboni Sutradhar - S401805

**Primary Contribution: Image Processing and OpenCV (`image_processor.py`)**

I developed the image-processing component of the puzzle game using **OpenCV and NumPy**. The `ImageProcessor` class is responsible for preparing images before they are converted into puzzle tiles and for reconstructing and visually decorating the puzzle board during gameplay.

My contribution includes the following functionality:

### Image Loading

The `load()` method safely loads image files and supports:

- JPG
- JPEG
- PNG
- BMP

The method checks whether the selected file exists and whether its extension is supported. It uses `numpy.fromfile()` together with `cv2.imdecode()` to load images, which also allows file paths containing non-English characters to work correctly on Windows.

A custom `ImageLoadError` exception is used to provide clear error messages when an image cannot be loaded.

### Image Preparation

The `prepare()` method prepares the selected image for the puzzle.

The image is first centre-cropped into a square so that the puzzle tiles remain square and the image is not stretched. It is then resized to fit the available display area.

The final image size is calculated as a multiple of the selected grid size. This ensures that every puzzle tile has exactly the same dimensions.

### Image Splitting

The `split()` method divides the prepared image into individual square tiles.

Each tile is stored using its original `(row, column)` position. A copy of each image section is created so that the individual tiles can later be manipulated independently by the puzzle game.

### Image Reassembly

The `assemble()` method reconstructs the current puzzle board from the tiles stored in the `TileGrid`.

It retrieves the displayed image from each tile, combines the tiles horizontally into rows, and then combines the rows vertically to produce one complete image.

### Gameplay Overlays

I also implemented the image overlays used by the game to provide visual feedback to the player.

These include:

- **Grid lines** to show the boundaries between puzzle tiles.
- **Selection border** to identify the tile currently selected by the player.
- **Hint circles** to indicate a position involved in a hint.
- **Green ticks** to indicate tiles that are correctly positioned.

The overlays are drawn using OpenCV functions such as `cv2.line()`, `cv2.rectangle()`, `cv2.circle()` and `cv2.polylines()`.

### Separation Between GUI and OpenCV

The `ImageProcessor` class keeps OpenCV operations separate from the Tkinter GUI. Instead of directly performing image-processing operations, the GUI can request a completed image from `ImageProcessor`.

This separation makes the project easier to maintain because image processing and user-interface functionality are handled by different components.

---

## Divya Malla - S406481

**Primary Contribution: Tkinter GUI and Gameplay Interface (`gui.py`)**

I worked on the graphical user interface of the image puzzle game using **Python Tkinter**. My work focused on displaying the puzzle, managing user interaction and connecting the interface with the game logic and image-processing components.

### Game Window and Controls

The `PuzzleApp` class builds the main game window and displays the original and scrambled puzzle images side by side. The interface includes **Load Image**, **New Round**, **Hint**, and **Solve** buttons, with choices for **3×3, 4×4 and 5×5** grids and game difficulty.

### Image Loading and Starting a Round

The `load_image()` method opens a file-selection dialog and passes the chosen file to `ImageProcessor`, displaying an error message if loading fails. The `new_round()` method prepares and splits the image, creates a `Game`, scrambles its tiles and refreshes the display.

### Mouse Interactions

The GUI converts mouse clicks into puzzle tile positions and passes the corresponding action to the `Game` class:

- **Left-click:** Select and swap tiles.
- **Right-click:** Rotate a tile 90 degrees clockwise (Control-click is supported on macOS).
- **Shift-click:** Flip a tile horizontally.

### Game Status and Timer

The status area shows the number of moves, tiles remaining, hints remaining, score and time left. The timer updates the status display each second and warns the player when time runs out.

### Hints, Solving and Feedback

The **Hint** button requests a hint from the game and displays guidance about the selected tile's position or orientation. The **Solve** button asks for confirmation before showing the solution. The interface also displays messages when a puzzle is completed, when the timer expires or when an unexpected error occurs.

### Rendering and Component Integration

The GUI requests the original and puzzle-board images from `ImageProcessor`, converts the OpenCV BGR images into a format Tkinter can display, and redraws the canvases after player actions. It leaves tile rules, scoring and game state to `Game`, while `ImageProcessor` handles the image operations. This keeps the interface separate from the underlying logic.

---

# Technologies Used

- **Python**
- **OpenCV (`cv2`)**
- **NumPy**
- **Tkinter**
- **Pillow (`PIL`)**
- **Object-Oriented Programming (OOP)**

---

# Project Structure

The project is divided into separate components so that different responsibilities can be managed independently.

- **Tile / Tile-related classes** — represent and manipulate individual puzzle pieces.
- **Tile Grid / Game classes** — manage the puzzle layout and game state.
- **`image_processor.py`** — handles image loading, preparation, splitting, reassembly and OpenCV overlays.
- **`gui.py`** — displays the game and handles player input and interface updates.

---
## Areeba Salahuddin - [S404018]

**Primary Contribution: Gameplay Logic and GUI Integration**

I developed the gameplay logic and connected the existing `Game` class functionality with the graphical user interface. My contribution focuses on updating the game information, handling hints and solving, and controlling the game when the puzzle is completed.

### Moves Counter

I connected the moves counter in the GUI to the `game.moves_made()` method.

The displayed number of moves is updated after the player makes a move so that the GUI always shows the current number of moves.

### Tiles Remaining

I connected the tiles remaining display to the `game.tiles_remain()` method.

This allows the GUI to show how many tiles still need to be placed in their correct positions.

### Hint Functionality

I implemented the Hint button using the `game.get_hint()` method.

The method returns the current tile position and its correct home position. A blue hint circle is displayed on both:

- The transformed puzzle image
- The original image

The hint circles are removed when the player makes the next move. The existing `game.hint_remain()` functionality is used to enforce the hint limit.

### Solve Functionality

I connected the Solve button to the `game.solve()` method.

The solve functionality resets the puzzle state, including the tiles, moves, hints and selection, allowing the game to return to its initial state.

### Completion Detection

I implemented completion checking using the `game.is_solved()` method.

When the puzzle is completed, further tile clicks are disabled so that the player cannot make additional moves after the game has been solved.

When a new image is loaded, the completed state is reset so that the player can start a new puzzle.

### GUI and Game Integration

The gameplay functionality is handled through the GUI while the existing `Game` class manages the underlying game state.

This keeps the game logic and user-interface responsibilities separated while allowing the GUI to display the current game state and respond to player actions.

### Testing

I tested the gameplay functionality to ensure that:

- The moves counter updates correctly.
- The number of remaining tiles is displayed correctly.
- Hints appear on both images.
- Hint circles disappear after the next move.
- The hint limit is respected.
- The Solve button resets the game.
- Completed puzzles prevent further tile movements.
- A new image allows the player to start again.

---
# Summary of Jordan's Contribution

**Name:** Jordan Then Ryan
**Student ID:** S405349  
**Main Responsibility:** OOP

My main contribution was in the development of OOP structure for the puzzle for other members and fixing bugs that the other members make in their code.

# Summary of Shraboni's Contribution

**Name:** Shraboni Sutradhar  
**Student ID:** S401805  
**Main Responsibility:** Image Processing and OpenCV

The main contribution was the development of `image_processor.py`, which provides the image-processing functionality required by the puzzle game. This component connects the original image with the puzzle system by preparing the image, dividing it into tiles, reconstructing the puzzle board and providing visual feedback through OpenCV overlays.

# Summary of Divya's Contribution

**Name:** Divya Malla  
**Student ID:** S406481  
**Main Responsibility:** Tkinter GUI and Gameplay Interface

My main contribution was developing the `gui.py` interface for the puzzle game. It provides image selection, puzzle settings, mouse controls, gameplay status, hints, the timer and solution controls, and connects the player-facing interface with the game and image-processing components.

# Summary of Areeba's Contribution

**Name:** Areeba Salahuddin  
**Student ID:** S404018  
**Main Responsibility:** Gameplay Logic and GUI Integration

The main contribution was connecting the existing `Game` functionality with the GUI. This included displaying moves and remaining tiles, implementing hints on both images, connecting the Solve button, and preventing further moves when the puzzle is completed.

