# Intentional lint violations for D3 failure-mode demonstration only.
# Do not import into the application.

import os,sys


def broken( x,y ):
    unused = 42
    return x+y
