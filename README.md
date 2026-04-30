*This project has been created as part of the 42 curriculum by elarue, wakhazza.*

# A-Maze-ing

## 📖 Description
**A-Maze-ing** is a Python-based procedural maze generator and solver. The project builds a perfect (or imperfect) maze from a given configuration file, ensures a guaranteed path from the entrance to the exit, and embeds a mandatory "42" shape made of walls in the center. 

It features an interactive ASCII terminal interface allowing users to regenerate the maze, view the shortest path solution in real-time, toggle themes, and export the maze data into a hexadecimal format.

---

## 🚀 Instructions

### Prerequisites
- Python 3.10 or higher.
- `pip` or `venv` for dependency management.

### Installation & Execution
A `Makefile` is provided to simplify the workflow:

1. **Install dependencies** (Pydantic, Build, etc.):
   ```bash
   make install
   ```
2. **Run the program**:
   ```bash
   make run
   # Or manually: python3 a_maze_ing.py config.txt
   ```
3. **Linting & Type Checking** (Flake8 & Mypy):
   ```bash
   make lint
   ```
4. **Clean cache and build files**:
   ```bash
   make clean
   ```

---

## ⚙️ Configuration File Format (`config.txt`)

The generator relies on a `.txt` configuration file. It uses a `KEY=VALUE` format. Lines starting with `#` are ignored.

**Mandatory Keys:**
- `WIDTH`: Width of the maze (in logical cells).
- `HEIGHT`: Height of the maze (in logical cells).
- `ENTRY`: Coordinates of the start point `x,y`.
- `EXIT`: Coordinates of the end point `x,y`.
- `OUTPUT_FILE`: Name of the text file where the hex output will be saved.
- `PERFECT`: Boolean (`True` or `False`). If `True`, the maze has exactly one path between any two cells. If `False`, random walls are broken to create loops.

**Optional Keys:**
- `SEED`: Integer used to reproduce the same maze generation. If omitted, a random seed is generated automatically.

**Example:**
```text
WIDTH=15
HEIGHT=15
ENTRY=0,0
EXIT=14,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

---

## 🧠 Algorithms & Technical Choices

### Maze Generation: Iterative DFS (Depth-First Search / Recursive Backtracker)
We chose an iterative **DFS** using a stack (`list` in Python) to generate the maze. 
- **Why?** The Recursive Backtracker is famous for creating long, winding corridors, which makes mazes visually appealing and fun to solve. We opted for the *iterative* version (with a stack) rather than the recursive one to prevent `RecursionError` on very large mazes, ensuring high stability.

### Maze Solving: BFS (Breadth-First Search)
To find the solution path, we implemented a **BFS**.
- **Why?** Unlike DFS, which might find *a* path, BFS guarantees finding the **shortest possible path** from the entry to the exit. It propagates like a wave, which is perfect for generating the final step-by-step directions (`N`, `S`, `E`, `W`) required in the hex export.

---

## 📦 Code Reusability (`mazegen` package)

The core logic of the maze generation has been isolated into a standalone module named `mazegen.py` to fulfill the reusability requirement.

### How to build and install it:
You can package this module into a `.whl` or `.tar.gz` file:
```bash
python3 -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### How to use it in your own code:
```python
from mazegen import MazeTester

# 1. Instantiate the generator
tester = MazeTester(width=20, height=12, entry=[0,0], exit_p=[19,11], is_perfect=True)

# 2. Generate the maze (optionally with a specific seed)
tester.generate(seed=42)

# 3. Solve the maze to get the shortest path
path = tester.solve()
print("Path coordinates:", path)

# 4. Export to standard 42 Hex format
tester.export_to_hex("my_output.txt")
```

---

## 🤝 Team & Project Management

### Roles
- **`elarue`**: Core Algorithmic Logic. Handled the DFS generation algorithm, the BFS solving algorithm, and the complex mathematical integration of the static "42" pattern within the dynamic grid.
- **`wakhazza`**: Architecture, Data, and UI. Managed the file parsing with `Pydantic` (error handling & data validation), the interactive terminal Menu (themes, colors, keyboard inputs), the `Makefile`, and the complex Hexadecimal data export logic.

### Planning & Evolution
We started by defining the data structures (lists of dictionaries to track the 4 cardinal walls of each cell). `elarue` focused on the backend generation while `wakhazza` built the frontend loop and the parser. We then merged our logic to connect the ASCII rendering to the logical grid.
- **What worked well**: Separating the "logical grid" from the "visual ASCII grid" allowed us to work in parallel without merge conflicts.
- **What could be improved**: One of the main challenges was creating smooth terminal animations without display glitches or flickering. Another difficulty was implementing the maze carving algorithm correctly, especially making sure that walls were removed consistently between neighbouring cells.

### Tools Used
- **Language**: Python 3.12
- **Libraries**: `pydantic` (for robust config validation), `sys`, `termios`, `tty` (for real-time keypress capture without pressing Enter).
- **Quality/Linting**: `flake8`, `mypy`.
- **Version Control**: Git & GitHub.

---

## 📚 Resources & AI Usage

### Resources
- Wikipedia: [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- Wikipedia: [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

### AI Usage Statement
During this project, Artificial Intelligence (LLM) was used strictly as an educational tutor and debugging assistant:
- **Task:** Understanding the BFS algorithm concepts.
- **Task:** Exploring how to capture single keystrokes in Python without requiring the user to press `Enter` (using `termios` and `tty`).
- **Task:** Reviewing code structure to ensure compliance and generating this README template based on our project details.
No full code files were blindly generated or copy-pasted; all algorithms were implemented and adapted manually to fit our specific grid structure.