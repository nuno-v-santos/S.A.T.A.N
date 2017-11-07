import runpy
import sys
import os


path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
runpy.run_module('secure-pc', run_name="__main__", alter_sys=True)