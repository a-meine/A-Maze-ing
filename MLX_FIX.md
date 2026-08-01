# Fixing the mlx_CLXV build in the Makefile

This document explains what went wrong while building the mlx Python wheel from the
upstream repo (`github.com/42school/mlx_CLXV`) and how the project Makefile was fixed.

The relevant top-level target (Makefile:54-71) clones the repo, patches its Makefile
with `sed`, builds, and cleans up:

```make
$(MLX): $(DEPENDECY)
	rm -rf mlx_CLXV
	git clone git@github.com:42school/mlx_CLXV.git
	cd mlx_CLXV && \
	LOCAL_PREFIX="$(PREFIX)" && \
	FILE="Makefile" && \
	grep -q "^LOCAL_PREFIX=" "$$FILE" || sed -i "/^NAME=/a LOCAL_PREFIX=$$LOCAL_PREFIX" "$$FILE"; \
	sed -i 's|^INCLUDES=.*|INCLUDES=-I./src -I$$(LOCAL_PREFIX)/include|' "$$FILE"; \
	sed -i 's|^override CFLAGS.*|& -L$$(LOCAL_PREFIX)/lib -Wl,-rpath,$$(LOCAL_PREFIX)/lib|' "$$FILE"; \
	sed -i 's|^all: config $$(NAME) pypkg|all: $$(NAME) pypkg|' "$$FILE"; \
	sed -i '/^config: configure.sh/,+1 s/^/# /' "$$FILE"; \
	sed -i '1 s|^#!/bin/sh|#!/usr/bin/env bash|' pybuild.sh
	sed -E -i 's/^( *mlx *= *\[[^]]*)(])/ \1, "py.typed"\2/' mlx_CLXV/python/pyproject.toml
	touch mlx_CLXV/python/src/mlx/py.typed
	cd mlx_CLXV && make
	cp mlx_CLXV/mlx-*.whl "$(MLX)"
	rm -rf mlx_CLXV
```

## Problem 1: linker cannot find `-lxcb-keysyms`

### Symptom

```
/usr/bin/ld: cannot find -lxcb-keysyms: No such file or directory
```

The library exists (`~/local/lib/libxcb-keysyms.so`, installed as a build
dependency of mlx), but the link command contained no `-L/home/nick/local/lib`,
so the linker never searched that directory.

### Root cause

The recipe's sed patch was supposed to append the `-L` flag to mlx's `LDFLAGS`:

```make
sed -i 's|^LDFLAGS.*|LDFLAGS+= -L$$(LOCAL_PREFIX)/lib -Wl,-rpath,$$(LOCAL_PREFIX)/lib|' "$$FILE";
```

Two independent reasons why this never took effect:

1. **`override` prefix.** Every `LDFLAGS` assignment in mlx's Makefile starts with
   `override` (e.g. `mlx_CLXV/Makefile:93`). The regex `^LDFLAGS.*` anchors at the
   start of the line, so it matched nothing. Upstream uses `override` deliberately so
   an external `make LDFLAGS=...` cannot silently clobber its flags
   (see the comment at `mlx_CLXV/Makefile:161-162`).

2. **Dead conditional block.** Rewriting the pattern to `^\(override \)\?LDFLAGS.*`
   made the patch land on the *right* line — but that line sits inside:

   ```make
   VULKAN_LOADER_PREFIX:=$(firstword $(foreach p,...,$(p)/lib/libvulkan.dylib...))
   ifneq ($(VULKAN_LOADER_PREFIX),)
   override LDFLAGS+= ... -L$(LOCAL_PREFIX)/lib -Wl,-rpath,$(LOCAL_PREFIX)/lib
   endif
   ```

   `VULKAN_LOADER_PREFIX` only matches a `.dylib` — i.e. it is only ever non-empty on
   macOS. On Linux the `ifneq` is false, the line never executes, and `LDFLAGS`
   remains empty at link time. (`make -n` confirmed the link command had no `-L` at
   all.)

### Solution

Patch an unconditional line instead. `override CFLAGS+= $(INCLUDES) $(VK_DEBUG) -fPIC -Wall -O3`
(`mlx_CLXV/Makefile:168`) always executes, and CFLAGS appears before `$(LIBS)` on the
link rule (`mlx_CLXV/Makefile:239`), so the `-L` is correctly positioned ahead of
`-lxcb-keysyms`. The `&` keeps the original line and appends the flags:

```make
sed -i 's|^override CFLAGS.*|& -L$$(LOCAL_PREFIX)/lib -Wl,-rpath,$$(LOCAL_PREFIX)/lib|' "$$FILE";
```

The embedded rpath also lets the built `libmlx.so` find `libxcb-keysyms.so.1` at
runtime, not just at link time.

## Problem 2: missing OS packages (compile-time errors)

### Symptoms

```
src/mlx_xpm.c:11:11: fatal error: 'bsd/bsd.h' file not found
src/gpu/mlx___vulkan_init.c:8:10: fatal error: 'vulkan/vulkan.h' file not found
```

### Root cause

A minimal Ubuntu install ships only the *runtime* libraries (`libbsd0`,
`libvulkan1`) but not the *development* headers. The required headers live in
separate `-dev` packages. This is an incomplete dependency on this OS, not a bug
in mlx_CLXV: its Makefile already links `-lbsd` and compiles the Vulkan init file
even when the XCB backend is used.

Note: after installing `libbsd-dev`, the header is not at `/usr/include/bsd/bsd.h`
but in the multiarch directory `/usr/include/x86_64-linux-gnu/bsd/bsd.h`, which is
on the default include path automatically.

### Solution

```bash
sudo apt install libbsd-dev libvulkan-dev
```

(Fedora equivalent: `sudo dnf install libbsd-devel vulkan-headers`.)

## Problem 3: the wheel was destroyed and the version drifted

### Symptom

The build succeeded but `make` kept rebuilding, and `uv sync` failed to find the
wheel.

### Root cause

1. `pybuild.sh` writes the wheel *inside* the clone (`mlx_CLXV/mlx-2.4-py3-none-any.whl`).
   The next recipe line, `rm -rf mlx_CLXV`, deleted it before anything copied it to
   the repo root, where pyproject.toml's path dependency expects it.
2. Upstream bumped its version from 2.2 to 2.4, but the top Makefile
   (`MLX = mlx-2.2-py3-none-any.whl`) and `pyproject.toml` still referenced 2.2.

### Solution

Copy the wheel out before removing the clone, and pin the current version:

```make
MLX = mlx-2.4-py3-none-any.whl
...
	cd mlx_CLXV && make
	cp mlx_CLXV/mlx-*.whl "$(MLX)"
	rm -rf mlx_CLXV
```

```toml
[tool.uv.sources]
mlx = { path = "mlx-2.4-py3-none-any.whl" }
```

## Problem 4: `uv` not installed

### Symptom

```
make: uv: No such file or directory
```

### Solution

Install uv (no sudo required):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

then run `make install` (`uv sync`) once so the environment contains the built
wheel and `pydantic`, and `make` / `make run` will start the game.

## Why the sed scripts use `$$` (and when they don't)

The recipe text is expanded twice: first by the top-level Make, then as a shell
script, and the patched file is parsed *again* by mlx's own Make.

- `$$FILE`, `$$LOCAL_PREFIX` — Make turns `$$` into a literal `$`; the *shell*
  expands it at runtime. The Make variable `$(FILE)` does not exist.
- `$(LOCAL_PREFIX)` inside the sed replacement — single `$` is correct here: it is
  literally written into mlx's Makefile, where mlx's Make expands its own
  `LOCAL_PREFIX` variable later.
- `$(MLX)`, `$(PREFIX)`, `$(DEPENDECY)` — expanded by the top-level Make at parse
  time, so they use a single `$`.

## Summary of fixes

| # | Where | Change |
|---|-------|--------|
| 1 | Makefile:62 | sed targets `override CFLAGS` (unconditional) instead of `LDFLAGS` (macOS-only block); `&` appends `-L` + rpath |
| 2 | system | `sudo apt install libbsd-dev libvulkan-dev` |
| 3 | Makefile:5,69-70 | `MLX = mlx-2.4-py3-none-any.whl`; `cp mlx_CLXV/mlx-*.whl "$(MLX)"` before `rm -rf mlx_CLXV` |
| 3 | pyproject.toml:17 | path dependency updated to `mlx-2.4-py3-none-any.whl` |
| 4 | system | install uv via the official installer |
