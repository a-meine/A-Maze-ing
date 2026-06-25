PREFIX := $(HOME)/local
SRC := $(PREFIX)/src
KEYSYMS_VER := 0.4.1
XCB_KEYSYMS := $(PREFIX)/include/xcb/xcb_keysyms.h
MLX := mlx-2.2-py3-none-any.whl

all: $(MLX)
	uv run a_maze_ing.py config.txt

$(MLX): $(XCB_KEYSYMS)
	rm -rf mlx_CLXV
	git clone git@github.com:42school/mlx_CLXV.git
	cd mlx_CLXV && \
	LOCAL_PREFIX="$(PREFIX)" && \
	FILE="Makefile" && \
	grep -q "^LOCAL_PREFIX=" "$$FILE" || sed -i "/^NAME=/a LOCAL_PREFIX=$$LOCAL_PREFIX" "$$FILE"; \
	sed -i 's|^INCLUDES=.*|INCLUDES=-I./src -I$$(LOCAL_PREFIX)/include|' "$$FILE"; \
	sed -i 's|^LDFLAGS.*|LDFLAGS+= -L$$(LOCAL_PREFIX)/lib -Wl,-rpath,$$(LOCAL_PREFIX)/lib|' "$$FILE"; \
	sed -i 's|^all: config $$(NAME) pypkg|all: $$(NAME) pypkg|' "$$FILE"; \
	sed -i '/^config: configure.sh/,+1 s/^/# /' "$$FILE"; \
	sed -i '1 s|^#!/bin/sh|#!/usr/bin/env bash|' pybuild.sh
	cd mlx_CLXV && make \
	&& cp mlx-2.2-py3-none-any.whl ../mlx-2.2-py3-none-any.whl
	rm -rf mlx_CLXV
	uv remove mlx
	uv add mlx-2.2-py3-none-any.whl

$(XCB_KEYSYMS):
	mkdir -p "$(SRC)"; \
	cd "$(SRC)" && \
	wget -nc https://xorg.freedesktop.org/archive/individual/lib/xcb-util-keysyms-$(KEYSYMS_VER).tar.xz && \
	rm -rf xcb-util-keysyms-$(KEYSYMS_VER) && \
	tar -xf xcb-util-keysyms-$(KEYSYMS_VER).tar.xz && \
	cd xcb-util-keysyms-$(KEYSYMS_VER) && \
	./configure --prefix="$(PREFIX)" && \
	make -j && \
	make install
	rm -rf "$(PREFIX)/src/xcb-util-keysyms-$(KEYSYMS_VER)"
	rm -f "$(PREFIX)/src/xcb-util-keysyms-$(KEYSYMS_VER).tar.xz"

clean:

fclean: clean
	rm -f $(XCB_KEYSYMS)

re: clean all

.PHONY: all clean fclean re
