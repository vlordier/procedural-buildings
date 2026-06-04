import sys

import numpy as np

# Designed to be run from the command line to turn a grammar into a .obj file
from ._logging import get_logger
from .Processor import Processor
from .Scope import Scope

log = get_logger(__name__)
if __name__ == "__main__":
    if len(sys.argv) != 12:
        log.error("bad args")
    else:
        gp = Processor()
        coords = [float(coord) for coord in sys.argv[1:7]]
        scope = Scope.freshScope(np.array(coords[:3]), np.array(coords[3:6]))
        gp.grammarToManyObjs(sys.argv[7], sys.argv[8], scope, int(sys.argv[9]), int(sys.argv[10]), sys.argv[11])
        log.info("Completed building generation")
