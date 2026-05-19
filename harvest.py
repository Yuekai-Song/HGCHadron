import os
import sys
from glob import glob
import argparse

edits = []
def UpdateIfExists(process, modName, attrName, newVal, prefix='process.'):
    if hasattr(process, modName):
        mod = getattr(process, modName)
        if hasattr(mod, attrName):
            attr = getattr(mod, attrName)
            prev = '%s' % attr
            newArg = type(attr)(newVal)

            attr.setValue(newVal)
            print('Updating %s.%s from %s to %s' % (modName, attrName, prev, getattr(mod, attrName)))
            edits.append('%s%s.%s = %s' % (prefix, modName, attrName, getattr(mod, attrName)))

def SetInputFileName(process, newName):
    fileNames = []
    for name in newName:
        fileNames.append('file:%s' % name)
    UpdateIfExists(process, 'source', 'fileNames', fileNames)

def UpdateConfig(inputCfg, outputCfg, inputFile=None):
    # Have to reset sys.argv here in case the inputCfg will do its own VarParsing
    # => this is a bit of a hack!
    sys.argv = [inputCfg]
    exec(compile(open(inputCfg, "rb").read(), inputCfg, 'exec'), globals())

    if inputFile is not None:
        SetInputFileName(process, inputFile)
    
    os.system('cp %s %s' % (inputCfg, outputCfg))
    with open(outputCfg) as ofile:
        cfg = ofile.read()
    cfg = cfg.replace('#{EDITS}', '\n'.join(edits))
    outFile = open(outputCfg, "w")
    outFile.write(cfg)
    outFile.close()

parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, default='electron_PU', help='directory of DQM files to be harvested')
args = parser.parse_args()

pwd = os.getcwd()
os.chdir(args.dir)
inputFile = glob('jobs/*inDQM*.root')
os.chdir(pwd)
inputCfg = 'step4.py'
outputCfg = os.path.join(args.dir, 'step4.py')
UpdateConfig(inputCfg, outputCfg, inputFile)