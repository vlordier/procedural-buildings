.PHONY: test lint example all

test:
	uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q

lint:
	ruff check procedural_buildings/ tests/ scripts/
	ruff format --check procedural_buildings/ tests/ scripts/

example:
	uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
		-i grammars/material_building \
		-o /tmp/example.obj \
		-s 0,0,0,8,8,12
	@echo "Written to /tmp/example.obj"

all: test lint example