import sys, os, importlib, traceback
print('cwd=', os.getcwd())
print('sys.path[0]=', sys.path[0])
print('config path exists=', os.path.isdir(os.path.join(os.getcwd(), 'config')))
print('listing cwd sample=', list(os.listdir('.'))[:20])
try:
    m = importlib.import_module('config')
    print('imported config module:', m)
except Exception:
    traceback.print_exc()
