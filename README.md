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
