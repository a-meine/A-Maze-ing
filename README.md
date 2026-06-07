

# Instruction

The .whl package has worng metadata and many not work, the alternative is to build from source:

activate your virtual environment
```bash
source venv_mlx/bin/activate
```


extract the source archive

```bash
tar -xzf mlx_CLXV-2.2.tgz
cd mlx_CLXV
```

build the project wheel from source
```bash
make
```
```bash
uv pip install mlx-2.2-py3-none-any.whl
```

test the install
```bash
python -c "from mlx.mlx import Mlx; print(Mlx)"
```
