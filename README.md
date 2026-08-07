*This project has been created as part of the 42 curriculum by ameine, mnououal.*

---

# A-Maze-ing — This is the way

## Description

A Python maze **generator**, **solver** and **visualiser**. It reads a plain-text
configuration file, randomly generates a maze, optionally reproduces it from a
seed, displays it interactively in a graphical window (MiniLibX / MLX), draws a
shortest path from the entrance to the exit, and writes the result to a file
using the subject's hexadecimal wall representation.

The project follows the `A-Maze-ing` subject: the generation logic is kept
fully independent of the GUI so it can be reused (and packaged) in future
projects.

### Goal and overview

- **Generate** random mazes — perfect mazes (exactly one path between entry and
  exit) using a recursive backtracker, and additional generators (Prim, Wilson).
- **Validate** the maze against the subject's constraints (connectivity,
  symmetric walls, borders closed, no 3×3 open areas, a visible "42" wall
  pattern).
- **Solve** the maze with a BFS shortest-path search.
- **Encode and export** the maze to the subject's hex output file (`WIDTH ×
  HEIGHT` hex digits, entry, exit, and the `N/E/S/W` direction path) — directly
  consumable by the provided `output_validator.py`.
- **Visualise** interactively in an MLX window: re-generate, show/hide the path,
  switch algorithms, and cycle the colour of the "42" pattern and of the walls —
  all from an on-screen menu.

---

# Instructions

## Requirements

- **Python 3.10 or newer** (`.python-version`)
- [uv](https://docs.astral.sh/uv/) as the package manager (used to build, sync
  and run the project). `pip`, `pipx` or `conda` would work too.

### Installing dependencies

```bash
make install     # equivalent to: uv sync
```

This installs the dependencies declared in `pyproject.toml` (`mlx` local wheel,
`mazegen` local wheel, `pydantic >= 2.13`) from the `uv.lock` lockfile. It also
pulls in the development tooling (`mypy`).

### Building the local packages (portable)

The two Python wheels are committed at the repository root and referenced as
local sources in `pyproject.toml`:

- `mlx-<version>-py3-none-any.whl` — the school's MiniLibX graphical library
  (Vulkan backend).
- `mazegen-1.0.0-py3-none-any.whl` — the reusable maze-generation package (this
  projects uses it as an in-repo dependency).

To **rebuild the maze generator wheel from the source** in the `maze/` folder:

```bash
uv sync
uv build maze --wheel --out-dir .   # produces mazegen-1.0.0-py3-none-any.whl
```

To **rebuild the MLX wheel from the upstream source** (optionally with a
different backend), the `Makefile` bundles this.

### Running the project

```bash
make run                      # equivalent to: uv run a_maze_ing.py config.txt
uv run a_maze_ing.py config.txt
```

`a_maze_ing.py` is the mandatory entry point and takes a single argument — the
**configuration file**:

```
Usage: python3 a_maze_ing.py config.txt
```

### Other useful targets (Makefile)

| Target        | Purpose                                                        |
|---------------|----------------------------------------------------------------|
| `make all`    | Build the local wheels and run the project                     |
| `make run`    | Run the visualiser on `config.txt`                             |
| `make debug`  | Run the main script under `pdb`                                |
| `make lint`   | `flake8` + `mypy` with the mandatory flags                     |
| `make lint-strict` | `uv run flake8 .` + `uv run mypy . --strict`           |
| `make clean`  | Remove `__pycache__`, `.mypy_cache`, `*.pyc`, `output_maze.txt` |
| `make fclean` | `clean` + remove the local MLX wheel                           |
| `make re`     | `clean` then `all`                                              |

### Validation script

The subject-provided `output_validator.py` checks the coherence of the generated
output file:

```bash
python3 output_validator.py output_maze.txt
```

### Tests

The project ships with an in-memory `FakeMlx` so the visualiser can be tested
without opening a window:

```bash
uv run pytest
```

Run the visualiser tests specifically:

```bash
uv run pytest tests/visualiser
```

---

# Configuration file

A configuration file must contain **one `KEY=VALUE` per line**. Lines starting
with `#` are comments and are ignored (lower/upper case is tolerated). Values
are stripped of surrounding whitespace; the parser validates types and bounds.

The mandatory keys are:

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width in number of cells | `WIDTH=20` |
| `HEIGHT` | Maze height in number of cells | `HEIGHT=20` |
| `ENTRY` | Entry coordinates `(x,y)` | `ENTRY=1,3` |
| `EXIT` | Exit coordinates `(x,y)` | `EXIT=12,15` |
| `OUTPUT_FILE` | Output file path | `OUTPUT_FILE=output_maze.txt` |
| `PERFECT` | Whether the maze must be perfect | `PERFECT=True` |

Optional keys used by this project:

| Key | Description | Example |
|-----|-------------|---------|
| `SEED` | Integer seed for reproducible generation | `SEED=42` |
| `ALGORITHM` | (intended) generation algorithm name — currently the algorithm is chosen from the UI, not the config | `ALGORITHM=dfs` |

A default configuration file (`config.txt`) is committed at the repository root.

### Validation rules

The configuration is parsed and validated with **Pydantic** (`config/parser.py`):

- All mandatory keys must be present.
- `WIDTH` and `HEIGHT` must be positive integers (`WIDTH ≤ 100`).
- `ENTRY` and `EXIT` are `x,y` integer tuples that must be **inside** the grid
  and **different** from each other, and must **not** fall on the "42" wall
  pattern.
- `PERFECT` must be a valid boolean.

Malformed configuration (missing key, a line without `=`, letters where numbers
are expected, an invalid boolean, a wrong `ENTRY`/`EXIT` format, a missing file)
is reported with a clear error message and the program never crashes with a
traceback.

---

# Maze generation

### The maze model

Every cell carries up to **4 walls** (`Walls.north/east/south/west`). Walls are
kept **symmetric** — when a wall is opened or closed on one cell the window of
the neighbouring cell is updated in a mirrored way, so the data is always
coherent. The outer border is never open because out-of-bounds neighbours are
treated as walls.

The grid also places a visible **"42" wall pattern** (a block of fully closed
cells in the middle of the maze) — the centrepiece of the visualiser. If the maze
is too small to host the pattern, a message is printed on the terminal instead
of a crash.

### The chosen algorithm: **DFS (recursive backtracker)**

The default generator is a **Depth-First Search / recursive backtracker**
(`maze/algorithms/generator/dfs.py`). Starting from the entry cell, it carves a
path by repeatedly picking a random unvisited neighbour, knocking down the wall
in between, and backtracking when dead-ended.

**Why this algorithm was chosen:**

- **Simplicity & readability** — a stack-based walk is easy to implement,
  verify, and explain during peer review.
- **It always produces a perfect maze.** Every cell is visited exactly once, so
  the result forms a spanning tree and there is exactly one path between any
  two cells — exactly what the subject requires for `PERFECT=True`.
- **Long winding corridors** — recursive backtracking tends to create long,
  twisting passages, which display nicely and demonstrate the algorithm's
  signature.
- **Trivially animatable.** The generator emits an event for every processed
  cell, which the visualiser uses to grow the maze live tile by tile.
- **Foundational knowledge** — it is the classic "recursive backtracker"
  covered by the widely cited Jamis Buck recap (see Resources).

### Additional algorithms (extension)

Two extra generators were implemented and are selectable in the GUI:

- **Randomised Prim's algorithm** (`randomised_prim.py`) — grows a single
  connected region by repeatedly punching a random frontier wall. Produces
  mazes with many short dead ends and a more "sprawling" character. The growing
  frontier is highlighted in pink while it streams, so the algorithm's behaviour
  is easy to follow step by step.
- **Wilson's algorithm** (`wilson.py`) — loop-erased random walks. Produces a
  more uniform-looking random spanning tree with no obvious bias.

All three share an abstract `GeneratorBase` that provides grid access and the
**event callback** used for streaming animation, so switching algorithm is just
wiring a different subclass.

### Solution

The shortest path from entry to exit is found with **BFS**
(`maze/algorithms/solution/bfs.py`) over open walls. It builds a tree of
parents and back-walks to rebuild the path, then marks the visited walkable
cells.

### Constraint verification

The maze is built to respect the subject's rules by construction:

- **Connectivity / no isolated cells** — spanning-tree generators cover every
  non-wall cell (the "42" block is the only excluded region, allowed by the
  subject).
- **External border walls** — out-of-bounds neighbours can never be opened.
- **Symmetric walls** — see the wall model above.
- **No 3×3 open areas / corridors no wider than 2** — perfect mazes have
  single-cell corridors by construction; a test probes for 3×3 open zones
  across all generators.
- **"42" pattern visible** — a closed-cell block is carved near the centre.

---

# Output file format

The maze is written to `OUTPUT_FILE` with **one hexadecimal digit per cell**.
Each digit encodes which walls are closed:

| Bit (LSB) | Direction |
|-----------|-----------|
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

A wall being closed sets the bit to `1`, open to `0`. For example `3` (binary
`0011`) means open to the south and west; `A` (binary `1010`) means closed to
the east and west.

The file layout is:

```
<HEIGHT rows of WIDTH hex digits>, one row per line
<empty line>
<entry_x,entry_y>
<exit_x,exit_y>
<shortest path as N/E/S/W directions>
```

Every line ends with `\n`. The encoding (`maze/encoding.py`) is designed to be
testable by the subject's moulinette and `output_validator.py`.

---

# Reusable maze generator module

The whole maze logic lives in the `maze/` package and is **independent of any
GUI** (it does not import `mlx`). This package is what gets built into the
`mazegen-1.0.0-py3-none-any.whl` wheel so it can be reused in a later project.

The public building blocks:

- `MazeGenerator` — a single facade to generate, solve and export a maze
  (validate parameters, seed, choose the algorithm, read the hex rows).
- `Grid` — the 2D grid of cells; access with `grid[y][x]`, iterate (yields
  non-wall cells), read `grid.start` / `grid.end` / `grid.pattern_cells()`.
- `Cell` / `Walls` — coordinates and the four per-cell wall booleans.
- `GeneratorBase` + `DFS`, `Prim`, `Wilson` — perfect-maze generators.
- `BFS` — shortest-path solver.

### Basic usage

```python
from maze import MazeGenerator, Grid, DFS, BFS

# One-class usage
gen = MazeGenerator(20, 15, entry=(1, 1), exit=(18, 13), seed=42).generate()
print(gen.hex_rows())          # list of WIDTH-char hex strings
print(gen.solution)            # [(x, y), ...] from entry to exit
print(gen.directions)          # 'NESW...' direction string

# Lower-level usage
grid = Grid.build(6, 6)        # 6×6, default entry (0,0) exit (5,5)
DFS(grid).generate_maze()      # carve the maze
path = BFS(grid).solve()       # shortest path
grid.show()                    # ASCII dump in the terminal
print(" -> ".join(str(c) for c in path))
```

### Custom parameters

```python
from maze import MazeGenerator

# Same grid, different seed / algorithm / entry-exit
gen = MazeGenerator(20, 20, entry=(1, 3), exit=(12, 15),
                    seed=42, algorithm="wilson")
gen.generate()
```

Invalid parameters (negative or zero dimensions, out-of-bounds entry/exit,
entry on the "42" block, an unknown algorithm) raise `ValueError` with a clear
message instead of crashing.

### Accessing the structure and a solution

```python
grid[2][3]                # the Cell at (3, 2)
grid.pattern_cells()      # cells that form the "42" wall block
BFS(grid).solve()         # list[Cell] from entry to exit
```

### Building / installing the package

```bash
uv build maze --wheel --out-dir .        # rebuild mazegen-1.0.0-py3-none-any.whl
uv add ./mazegen-1.0.0-py3-none-any.whl  # or: pip install ./mazegen-1.0.0-py3-none-any.whl
```

The wheel is also referenced as a local dependency in the root `pyproject.toml`,
so `uv sync` pulls it in automatically. The full documentation inside the
package is also mirrored in this `README.md`.

---

# Visual representation (MLX)

The project ships a full **graphical (MLX)** visualiser rather than only
terminal ASCII. It opens a full-HD (1920×1000) window, splits the screen into a
left-hand menu panel and a right-hand maze panel, and renders the maze by
compositing every tile into a **single pixel buffer** (`maze_canvas_img`) that is
presented with one draw call.

### Rendering and the "single-canvas" design

The installed MLX (Vulkan backend) has an internal **limit of ~64 draw calls
between two synchronisations**. Drawing each tile or each character of a label
counts as a separate call; exceeding the limit forces an auto-flush mid-frame
and a black background flash. To respect this, the project:

- composites the entire maze (every tile + the "42" pattern + the path + entry
  / exit) into one canvas buffer using raw pixel writes, and presents it once;
- paints every menu widget rectangle into a single `menu_canvas_img` and only
  draws the text labels on top, keeping the per-frame count under 64.

This single-vsync `present_scene()` approach guarantees the menu and the maze
appear together on every frame without artefacts.

### Side interactions (menu)

All interactions are handled with the mouse (left-click) on the on-screen menu:

- **Apply** — apply the current size and entry/exit values in the input fields.
- **Regen** — generate (and solve, and re-export) a brand new maze.
- **Hide/Show** — toggle the visibility of the shortest path.
- **DFS / Prim / Wil** — switch the generation algorithm.
- **Maroon / Mauve / Sapphire** — cycle the colour of the "42" pattern.
- **Gray / Teal / Sapphire / Maroon / Mauve** — cycle the maze **wall colour**.
- **CRAZY** — generate each algorithm once (3 mazes total), then cycle through
  every combination of "42" pattern colour and wall colour (3 × 5) without
  regenerating (a demonstration loop).
- **exit** — close the window.

The mandatory interactions (re-generate, show/hide a valid shortest path, change
wall colours) are all available, the "42" pattern has a dedicated colour cycler,
and the width/height/entry/exit can be edited live.

### Architecture overview

```
a_maze_ing.py              entry point  ->  load_config()  ->  App(config).run()
   |
   +-- config/parser.py     Pydantic Config model + load_config()
   +-- maze/                (pure logic, no GUI)
   |    cell.py  walls.py  coordinate.py  direction.py  grid.py
   |    algorithms/generator/{dfs, randomised_prim, wilson}.py
   |    algorithms/solution/bfs.py
   |    encoding.py         hex-encode + write the output file
   +-- visualiser/          (MLX GUI, shares one WindowContext)
        app.py       orchestrator + menu actions
        context.py   owns the mlx window/pointers/state
        renderer.py  composites the maze into a single canvas
        maze.py      MazeEngine: builds the grid, wires the event, solves
        menu.py      builds/redraws the widgets
        input.py     mouse + keyboard hooks
        widgets.py   Button, InputField, fill helpers
        layout.py    geometry math
        constants.py  MlxColor.py  (Catppuccin palette)
```

The design keeps the **maze core decoupled from the GUI**: the visualiser is
the only consumer of `mlx`, and the generator talks back to the renderer only
through an `event` callback that is used for animation.

---

# Architecture: separation of concerns and the event-driven bridge

This section details how the maze logic and the GUI are separated and re-linked,
how the generator logic evolved into an event-driven pipeline, and how the
overall structure is classified from a *Separation of Concerns* point of view.

### Overview: the publish / subscribe interaction flow

The diagram below walks through one full cycle — from a user click to the
on-screen redraw — to show how the GUI and the maze logic communicate. The
*seam* is the **subscribe → publish → update → redraw** loop between the
generator (subject) and the renderer (observer).

```
  CONTROLLER                 MODEL (subject)                VIEW (observer)              MLX / STATE
  App · InputHandler         maze/ generators               Renderer · Menu              WindowContext

     │  user clicks "Regen"                                   │                                │
     ▼                                                        │                                │
  1. regen()  ──────────────────────────┐                     │                                │
     │        build Grid, pick algo     │                     │                                │
     │        (DFS / Prim / Wilson)     ▼                     │                                │
    └───────────────────────────────► MazeEngine          subscribe                            │
                                        │                     │                                │
2. SUBSCRIBE                         │  generator.event  ──► │                                 │
     wire renderer to generator        │  = renderer.render   │   renderer now listens         │
                                        │                     │                                │
  3. grid.generate_maze()  ────────────► │                     │                               │
     (Controller drives the Model)      ▼  loop over cells    │                                │
                                        │                     │                                │
  4. PUBLISH (per carved cell)          │  _trigger_event(cell)─► render(cell) ─────────────►  │
     the model pushes one cell          │                     │  paint a few tiles             │
     to every subscriber                │                     │  present_scene()               │
                                        │                     │  ───────────► mlx_sync()       │
                                        │                     │               (draw one frame) │
                                        ▼                     │                    │ redraw    │
  5. until maze is complete             │                     │                    ▼           │
                                        │                     │                                │
     ─────────────────────────────────  │                     │                                │
  6. Controller solves + exports        │                     │                                │
     BFS(solve)  → solution_path  ◄─────│──────────────────────│──────────────────────────────│─► state
     write_output()  → output file      │                     │                              │
                                        │                     │                              │
  7. REDRAW  render_maze()  ────────────│─────────────────────►│  walls + 42 + path + entry    │
     (final full paint)                 │                     │  + exit, present_scene()      │
                                        │                     │  ─────────► mlx_sync()  redraw│
                                        │                     │                    ▼          │
  8. ...back to the event loop,         │                     │                window          │
     waiting for the next click        ────────────────────────   (mlx_loop)                   │
```

Reading order:

1. **Trigger** — the `InputHandler` calls a controller action (`regen()`).
2. **Subscribe** — `App` injects `Renderer.render` into the engine; the engine
   sets `generator.event = renderer.render`. The renderer becomes a subscriber.
3. **Drive** — the controller starts `generate_maze()` on the model.
4. **Publish** — for every carved cell the generator emits
   `_trigger_event(cell)`; the subscribed renderer reacts.
5. **Update / redraw** — `Renderer.render(cell)` paints the surrounding tiles
   and asks `WindowContext.present_scene()` to flush (`mlx_sync`) one frame.
6. **Solve + export** — BFS fills `solution_path`; `write_output()` saves the
   hex file.
7. **Final redraw** — `render_maze()` paints the whole scene (walls, "42",
   path, entry/exit) once more.
8. **Idle** — control returns to `mlx_loop()` until the next input.

The model only ever calls an *optional* callback, so a headless consumer (e.g.
`MazeGenerator.generate()` or a terminal test) that never subscribes runs the
very same carving loops with no GUI at all.

## The SoC model (MVC hybrid with a shared context)

The project is built as a pragmatic **Model–View–Controller** layered on a
central shared-context hub. Concretely:

| Concern | Code | Responsibility |
|---|---|---|
| **Model** | `maze/` (`Grid`, `MazeGenerator`, generators, `BFS`, `encoding`) | maze state and algorithms only. Pure Python, no GUI imports, no knowledge of windows or pixels. |
| **View** | `visualiser/Renderer`, `Menu`, `Widgets` | paints the maze grid and the on-screen widgets from state. |
| **Controller** | `visualiser/App`, `InputHandler` | turns user actions into orchestrations and wires the View to the Model. |
| **Shared context** | `visualiser/WindowContext` | holds every piece of runtime state the View reads (`show_path`, `algorithm`, `pattern_color`, `wall_color`, `solution_path`, `entry`, `exit`) plus thin `mlx` helpers. |

Because that context is a central "data-to-bind-the-view" state holder, parts of
the code feel **ViewModel**-like (MVVM: state the View binds to, kept apart from
the `mlx` window). However, an explicit controller for input and orchestration
keeps the whole thing recognisably **Model–View–Controller**. The honest label
is therefore a **hybrid**: MVC driven by a shared context (sometimes called
"Model-View-Controller + shared/blackboard state").

All coupling between components runs through `WindowContext` by dependency
injection in the constructors — no component imports another component's
internals. This is what makes the visualiser unit-testable headless with a
`FakeMlx` (the tests inject a fake `mlx` into the very same `WindowContext`).

## The single seam between GUI and maze logic

The only place the Model and the View touch is **one optional callback** on the
generator base class (`maze/algorithms/generator/base.py`):

```python
event: Callable[[Cell, bool], None] | None = None

def _trigger_event(self, cell: Cell, sync: bool = True) -> None:
    if self.event is not None:
        self.event(cell, sync)      # optional push to whoever subscribed
```

The GUI subscribes that callback through the controller:

```python
# App composes the engine with the renderer's paint function
self.engine = MazeEngine(self.ctx, self.renderer.render)

# MazeEngine.config_images() attaches the renderer to the generator
ctx.grid.event = self._render_cb
```

Consequences of that single seam:

- the **model never imports the view** — it only invokes an optional callable;
- the **view never imports the model** — it receives a `Cell` and repaints a
  few pixels through `present_scene()`;
- the **controller does the wiring** — passing `renderer.render` into the
  engine, which attaches it to the generator's `event`.

## Evolution: from "a generator object" to event-driven control

**Phase 1 — a blocking generator object.** The maze package originally exposed a
generator over a grid that runs to completion:

```python
gen = DFS(grid)
gen.generate_maze()     # blocks until the whole maze is carved
# then the console/UI draws the finished result
```

The caller could only ever see the *final* maze.

**Phase 2 — event-driven streaming.** To be able to *animate* the generation, an
`event` hook was added to `GeneratorBase`. Every time a cell is processed, the
generator emits it (`_trigger_event(cell)`), the renderer repaints that area and
syncs once per event, so the maze visibly grows **one tile at a time** with a
bounded number of draw calls per frame.

This is an application of the **observer pattern**: the subject (a generator)
emits cells; the **observer** (`Renderer`) reacts; the generator stays agnostic
of whom it notifies. The emitted callback also carries a `sync` hint (`True`
for a "present now", `False` to allow batching) that the observer may use to
coalesce updates.

Because the event is optional, the headless `MazeGenerator.generate()` facade
attaches **no** listener and stays fully silent and reusable — the exact same
carving loops drive either a terminal print (headless) or a live window (GUI).

---

# Resources

### Classic references

- [Maze Generation: Algorithm Recap — Jamis Buck](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap) — the canonical recap of all the classic generation algorithms (DFS, Prim, Kruskal, Wilson…).


### How AI was used

AI was used as an assistant during development, on specific and verifiable
tasks, always reviewed and understood before being integrated:

- **Configuration validation design** — helped brainstorm a Pydantic-based
  validation approach instead of a hand-rolled parser, and to reason about the
  trade-off between `@dataclass` and a validated model for untrusted input.
- **Algorithm theory clarification** — used to compare the DFS, Prim and
  Wilson generators (correctness, maze texture, animation) and to double-check
  the loop-erased random walk logic in Wilson.
- **Rendering strategy brainstorming** — used to explore options for the MLX
  "black background" bug (the 64-draw limit) and to evaluate a single-canvas
  compositing approach over per-tile draws.
- **Test scaffolding** — helped draft pytest fixtures and the in-memory
  `FakeMlx` so the visualiser could be tested without a window.
- **Documentation polish** — helped draft and proofread this README and the
  package README.

AI was **not** used for any core algorithm without a peer explanation: the maze
generation routines, the BFS solver, the hex encoding, and the MLX rendering
were all written, discussed, and verified with peers before integration.

---

# Team and project management

### Team, roles

| Team member | Focus |
|-------------|-------|
| **mnououal)** | Maze core logic, configuration validation, BFS solver and encoding/output, tests, package build and documentation. |
| **ameine** | MLX integration, the visualiser/*, menu interactions, the layout geometry, Makefile and the MLX build/rendering fixes. |

Division of work was oriented around the two big pillars of the project
(model vs. the GUI), which the repository structure (a GUI-free `maze/`
package next to the `visualiser/`) reflects.


### What worked well and what could be improved

**Worked well:**

- A clean, layered architecture with the maze logic fully separated from the GUI.
- Three working, tested generation algorithms plus BFS solver and correct hex
  output — the output file validates with the provided script.
- Flake8 and mypy pass on the committed repository; docstrings on all modules.
- A pragmatic solution to the (only) hard problem: single-canvas compositing
  under the MLX 64-draw limit.
- Solid test suite (the visualiser tested against an in-memory fake).

**Could be improved:**

- An imperfect (looping) maze is **not** implemented. This is a deliberate
  scope decision, not an oversight: the subject only requires a *perfect* maze
  when `PERFECT=True`, and it does **not** require an imperfect maze when the
  flag is unset — so all generators always produce perfect mazes (spanning
  trees). A looping non-perfect mode would be the obvious extension.
- The UI `WIDTH`/`HEIGHT`/`ENTRY`/`EXIT` input fields do not yet fully control
  grid geometry (layout sizing still primarily driven by the config).
- The `mazegen-*.whl` is rebuilt from the `maze/` source by `make`/`uv build`
  (keep it in sync when the core code changes).


### Tools used

- **Python 3.10** with **uv** for dependency management, sync and lockfiles.
- **Pydantic 2.x** for strict, typed configuration validation.
- **MLX** (the school's MiniLibX) Vulkan-backed graphical library — window,
  images, events, single-batch present.
- **pytest** with an in-memory `FakeMlx` for the visualiser.
- **flake8** (`select = F,N`) and **mypy --strict** for static checking.
- **Git** for branching (a `maze`-logic branch and a `visualiser` branch were
  merged) and code review.

---

# Known limitations

1. An imperfect/looping maze is not implemented. The subject only requires a
   perfect maze when `PERFECT=True`; it does not require an imperfect maze when
   the flag is unset, so every generator always produces a perfect maze.
2. The `ALGORITHM` config key is not read — the algorithm is selected via the
   on-screen menu.
3. The `mazegen-*.whl` at the root is built from the current `maze/` source —
   rebuild it (see Instructions) whenever the `maze/` code changes so the
   committed wheel stays in sync.
