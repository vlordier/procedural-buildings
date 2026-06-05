# Architecture

## Data Flow

```
Grammar file (.grammar)
        │
        ▼
┌────────────────┐
│   Lexer        │  SLY-based tokeniser
│   Parser       │  SLY-based LALR(1) parser → rule dict
│   Checker      │  Resolves rule references, builds op graph
│   GrammarVars  │  Expression evaluation (sympy-backed)
└───────┬────────┘
        │ Op graph (Op tree)
        ▼
┌────────────────┐
│   Processor    │  Runs op.run(context, scope, env) recursively
│   Ops.py       │  16 Op subclasses (split, repeat, colour, etc.)
│   Scope.py     │  Scope propagation, transforms, splits
│   ContextObj   │  Accumulates primitives and renders to .obj
└───────┬────────┘
        │ .obj file
        ▼
┌────────────────┐
│   Viewer       │  Pyglet-based 3D viewer (procedural_buildings/view.py)
│   obj_to_glb.py│  OBJ → glTF/GLB conversion
└────────────────┘

## Reverse Path

```
.obj file
        │
        ▼
┌────────────────┐
│   ObjReader    │  Reads .obj, extracts vertex data per primitive
│   BoxSplitter  │  Spatial splitter: boxes → Container tree → Op tree
│   simplify     │  Merges duplicate ops, produces minimal grammar
│   toGrammarText│  Serialises op tree back to grammar text
└───────┬────────┘
        │ Grammar file
        ▼
```

## Key Abstractions

- **Scope**: Position + rotation + size of a shape in 3D space
- **Op**: A shape-rewriting operation (split, repeat, colour, etc.)
- **Args**: Type-aware argument container with sympy expression evaluation
- **ContextObj**: Accumulator that collects primitives and writes .obj
- **Box**: A bounding box in 3D, linked to a primitive op
- **Container**: A spatial partition of boxes along an axis

## Environment (env dict)

The env dict flows through the op tree and carries:
- width/depth/height of the current scope
- neighbour info (left_width, right_width, etc.) for adaptive rules
- User-set variables via OpSetParams
- Grammar variable overrides via gin-config