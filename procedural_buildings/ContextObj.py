from ._constants import COLOUR_FMT_PRECISION
from .Primitive import basicPrims


class ContextOBJ:
    # Create a new context with prims being the set of known primitives
    def __init__(self, prims=basicPrims):
        self.objFileText = []
        self.prims = prims
        self.vertCount = 0
        self.currentColour = None

    # Insert the given primitive into our object data
    # The position, size and orientation of the primitive depends on scope
    def addPrim(self, primName, scope):
        if primName not in self.prims:
            print(f"Failed to find prim with name: {primName}")
            print(f"Available prims:\n{self.prims.keys()}")
            if "rect" not in self.prims:
                raise KeyError(f"No fallback primitive 'rect' available. Primitives found: {list(self.prims.keys())}")
            print("Just going to use a box")
            prim = self.prims["rect"]
        else:
            prim = self.prims[primName]
        newVerts = scope.putVertsInScope(prim.verts, prim.boundingBox)
        self.objFileText.append(f"o {primName}")
        if self.currentColour:
            self.objFileText.append(
                f" # colour({self.currentColour[0]:.{COLOUR_FMT_PRECISION}f},{self.currentColour[1]:.{COLOUR_FMT_PRECISION}f},{self.currentColour[2]:.{COLOUR_FMT_PRECISION}f})"
            )
        self.objFileText.append("\n")
        self.objFileText.extend(self.vertsToObjText(newVerts))
        self.objFileText.extend(prim.otherData)
        # Add the prim's face data but make sure the faces reference the correct
        # vertices by offsetting the vertex indices
        self.objFileText.extend(self.offsetVertIndices(prim.faceData))
        self.vertCount += prim.numVerts

    # Format a list of vertices for a .obj file
    def vertsToObjText(self, vs):
        return (f"v {coords}\n" for coords in [" ".join([f"{c:.5f}" for c in xyz[:3]]) for xyz in vs])

    # Write the current object to a file
    def writeToFile(self, fname):
        try:
            with open(fname, "w") as f:
                f.writelines(self.objFileText)
        except OSError:
            print(f"Failed to write to .obj file: {fname}")

    # The faces in a .obj file reference the vertex indices in a file
    # We need to offset these indices since other primitive shapes may
    # Appear before this one in the file
    def offsetVertIndices(self, faceData):
        faceLines = []
        for face in faceData:
            faceText = "f "
            for vertData in face:
                faceText += str(int(vertData[0]) + self.vertCount)
                for d in vertData[1:]:
                    faceText += f"/{d}"
                faceText += " "
            faceText += "\n"
            faceLines.append(faceText)
        return faceLines

    def reset(self):
        self.objFileText = []
        self.vertCount = 0
        self.currentColour = None

    def colour(self, col, scope):
        self.currentColour = col
