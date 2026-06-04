import getopt
import logging
import sys
from os import getcwd
from os import sep as path_sep

import gin
import numpy as np

from ._constants import DEFAULT_SCOPE_SIZE, DEFAULT_SEPARATION, NUM_SCOPE_COORDS
from ._logging import get_logger, setup_logging
from .Processor import Processor
from .Scope import Scope

log = get_logger(__name__)


def main(argv):
    inFile = ""
    outFile = ""
    rev = False
    n = 1
    sep = DEFAULT_SEPARATION
    filePerObj = False
    startRule = "plot"
    startScope = Scope.freshScope(np.array([0, 0, 0]), np.array(DEFAULT_SCOPE_SIZE))
    ginFiles = []
    ginParams = []
    verbose = False
    usage = (
        "Usage:\nprocedural_buildings -i <input_file> -o <output_file>"
        " [-s | --start_scope <x_min,y_min,z_min,x_max,y_max,z_max>]"
        " [-R | --start_rule <start_rule>] [-r | --reverse]"
        " [-n <num_buildings>] [-d | --separation <separation_distance>]"
        " [-f | --file_per_obj] [-g | --gin_file <config.gin>]"
        " [-p | --gin_param <bindings>] [-v | --verbose]"
    )
    try:
        opts, _args = getopt.getopt(
            argv,
            "hi:o:s:R:rn:d:fg:p:v",
            [
                "ifile=",
                "ofile=",
                "start_scope=",
                "start_rule=",
                "reverse",
                "separation=",
                "file_per_obj",
                "gin_file=",
                "gin_param=",
                "verbose",
            ],
        )
    except getopt.GetoptError:
        log.error("Option error")
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inFile = arg
        elif opt in ("-o", "--ofile"):
            outFile = arg
        elif opt in ("-s", "--start_scope"):
            try:
                coords = [int(coord) for coord in arg.split(",")]
                assert len(coords) == NUM_SCOPE_COORDS
                startScope = Scope.freshScope(np.array(coords[:3]), np.array(coords[3:]))
            except (ValueError, AssertionError):
                log.error("Invalid scope argument.")
                print(usage)
                sys.exit()
        elif opt in ("-R", "--start_rule"):
            startRule = arg
        elif opt in ("-r", "--reverse"):
            rev = True
        elif opt == "-n":
            try:
                n = int(arg)
                if n < 1:
                    log.error("Error: -n must be a positive integer")
                    sys.exit(2)
            except ValueError:
                log.error("Error: -n must be a positive integer")
                sys.exit(2)
        elif opt in ("-d", "--separation"):
            try:
                sep = float(arg)
                if sep < 0:
                    sep = 0
            except ValueError:
                log.error("Error: -d must be a number")
                sys.exit(2)
        elif opt in ("-f", "--file_per_obj"):
            filePerObj = True
        elif opt in ("-g", "--gin_file"):
            ginFiles.append(arg)
        elif opt in ("-p", "--gin_param"):
            ginParams.append(arg)
        elif opt in ("-v", "--verbose"):
            verbose = True

    if verbose:
        setup_logging(logging.DEBUG)

    if not inFile or not outFile:
        log.error("Please provide both an input and output file")
        print(usage)
        sys.exit()

    gin.parse_config_files_and_bindings(ginFiles, ginParams)

    p = Processor()
    if not ginFiles:
        p.grammarDir = getcwd() + path_sep
        p.outputDir = p.grammarDir
        p.engineeredDir = p.grammarDir
    if rev:
        if inFile.split(".")[-1] == "obj":
            objFiles = [inFile]
        else:
            with open(inFile) as f:
                objFiles = f.read().splitlines()
        p.objsToGrammar(objFiles, outFile)
    else:
        if filePerObj:
            p.grammarToManyObjFiles(inFile, startRule, startScope, n, outFile)
        else:
            p.grammarToManyObjs(inFile, startRule, startScope, n, sep, outFile)


if __name__ == "__main__":
    main(sys.argv[1:])
