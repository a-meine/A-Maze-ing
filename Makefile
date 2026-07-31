.PHONY: all deps mlx clean fclean re install run debug lint lint-strict
PREFIX := $(HOME)/local
SRC := $(PREFIX)/src
KEYSYMS_VER := 0.4.1
MLX = mlx-2.2-py3-none-any.whl
DEPENDECY = $(PREFIX)/include/xcb/xcb_keysyms.h

all: $(MLX)
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
	rm -rf "$(PREFIX)/src/xcb-util-keysyms-$(KEYSYMS_VER)"
	rm -f "$(PREFIX)/src/xcb-util-keysyms-$(KEYSYMS_VER).tar.xz"
	rm $(MLX)

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

re: clean all

$(DEPENDECY):
	@if [ ! -f "$(PREFIX)/include/xcb/xcb_keysyms.h" ]; then \
		mkdir -p "$(SRC)"; \
		cd "$(SRC)" && \
		wget -nc https://xorg.freedesktop.org/archive/individual/lib/xcb-util-keysyms-$(KEYSYMS_VER).tar.xz && \
		rm -rf xcb-util-keysyms-$(KEYSYMS_VER) && \
		tar -xf xcb-util-keysyms-$(KEYSYMS_VER).tar.xz && \
		cd xcb-util-keysyms-$(KEYSYMS_VER) && \
		./configure --prefix="$(PREFIX)" && \
		make -j && \
		make install; \
	fi

$(MLX): $(DEPENDECY)
	rm -rf mlx_CLXV
	it clone git@github.com:42school/mlx_CLXV.git
	cd mlx_CLXV && \
	LOCAL_PREFIX="$(PREFIX)" && \
	FILE="Makefile" && \
	grep -q "^LOCAL_PREFIX=" "$$FILE" || sed -i "/^NAME=/a LOCAL_PREFIX=$$LOCAL_PREFIX" "$$FILE"; \
	sed -i 's|^INCLUDES=.*|INCLUDES=-I./src -I$$(LOCAL_PREFIX)/include|' "$$FILE"; \
	sed -i 's|^LDFLAGS.*|LDFLAGS+= -L$$(LOCAL_PREFIX)/lib -Wl,-rpath,$$(LOCAL_PREFIX)/lib|' "$$FILE"; \
	sed -i 's|^all: config $$(NAME) pypkg|all: $$(NAME) pypkg|' "$$FILE"; \
	sed -i '/^config: configure.sh/,+1 s/^/# /' "$$FILE"; \
	sed -i '1 s|^#!/bin/sh|#!/usr/bin/env bash|' pybuild.sh
	sed -E -i 's/^( *mlx *= *\[[^]]*)(])/ \1, "py.typed"\2/' mlx_CLXV/python/pyproject.toml
	touch mlx_CLXV/python/src/mlx/py.typed
	cd mlx_CLXV && make
	rm -rf mlx_CLXV
