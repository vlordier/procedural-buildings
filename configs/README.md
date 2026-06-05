# Gin Configs

Grammar parameters (colours, sizes, counts) can be overridden at runtime
using [gin-config](https://github.com/google/gin-config) files.

## Usage

```bash
python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/checker.obj \
  -s 0,0,0,8,8,12 \
  -g configs/checker.gin
```

Or override inline without a file:

```bash
python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/custom.obj \
  -s 0,0,0,8,8,12 \
  -p 'grammar_var_overrides.values = {"wallPattern": 2, "wallR": 0.8}'
```

## Available configs

| Config | For grammar | Effect |
|---|---|---|
| `brick.gin` | `material_building` | Solid brick wall, dark roof |
| `nordic.gin` | `material_building` | White wall, blue horizontal stripe |
| `checker.gin` | `material_building` | Cream + brown checkerboard |
| `gradient.gin` | `material_building` | White-to-blue gradient |
| `soviet_9story.gin` | `soviet_block` | 9-story panel block |

## How to write a new config

```gin
grammar_var_overrides.values = {
    "wallPattern": 1,
    "wallR": 0.95,
    "wallG": 0.92,
    "wallB": 0.88,
    "stripeW": 0.1,
}
```

The variable names must match the `name = value` declarations in the
grammar file. All numeric types (int, float) are supported.