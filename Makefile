.PHONY: all deps clean fclean re install run debug lint lint-strict
MLX = mlx-2.4-py3-none-any.whl
MAZE = mazegen-1.0.0-py3-none-any.whl

all: $(MLX) $(MAZE)
	uv run a_maze_ing.py config.txt

install:
	uv sync

run:
	uv run a_maze_ing.py config.txt

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f output_maze.txt

fclean: clean
	rm $(MLX)

lint:
	uv run flake8 --extend-select=N .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

re: clean all

$(MAZE):
	uv build maze --wheel --out-dir .
	uv remove mazegen || true
	uv add $(MAZE)
	uv sync

$(MLX):
	rm -rf mlx_CLXV
	git clone git@github.com:42school/mlx_CLXV.git
	cd mlx_CLXV && BACKEND=wayland make
	cp mlx_CLXV/mlx-*.whl .
	rm -rf mlx_CLXV
	uv remove mlx || true
	uv add $(MLX)
	uv sync