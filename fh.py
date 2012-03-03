#!/usr/bin/python
#
# fh.py
#
"""
Usage: fh [_](=|+|-|cp|mv|ls) [file list]
"""

# imports
# =======

import os.path
import shutil
import sys


# functions
# =========

def stackFilename(): return os.path.expanduser("~/.fhstack")

def readStack():
  stack = []
  fname = stackFilename()
  if not os.path.exists(fname): return stack
  f = open(fname)
  fileset = []
  for line in f:
    if line == "===\n":
      stack.append(fileset)
      fileset = []
      continue
    fileset.append(eval(line))
  f.close()
  return stack

def writeStack(stack):
  stackFile = open(stackFilename(), 'w')
  for fileset in stack:
    for f in fileset: stackFile.write("%s\n" % `f`)
    stackFile.write("===\n")
  stackFile.close()

def showUsageAndExit(exitCode):
  print __doc__
  exit(exitCode)

def makeFileset(paths, ch):
  return [pathEntry(p, ch) for p in paths]

def pathEntry(p, ch):
  absPath = os.path.abspath(p)
  # Make sure directories end with /
  if os.path.isdir(p) and not p.endswith(os.sep): absPath += os.sep
  relPath = os.path.relpath(p)
  if relPath.startswith('..'):
    print "Paths can't be outside this directory (%s)" % relPath
    exit(1)
  return (ch, absPath, relPath)

def pushNewFilelist(filelist):
  stack = readStack()
  stack.insert(0, makeFileset(filelist, '+'))
  writeStack(stack)

def addFilelist(filelist):
  stack = readStack()
  if not stack:
    pushNewFilelist(filelist)
    return
  stack[-1] += makeFileset(filelist, '+')
  writeStack(stack)

def excludeFilelist(filelist):
  stack = readStack()
  if not stack:
    print "Error: no file list to exclude from"
    exit(1)
  stack[-1] += makeFileset(filelist, '-')
  writeStack(stack)

# Same format as user input. 
def topFileset(pop=False):
  stack = readStack()
  top = stack[-1] if stack else None
  if pop: writeStack(stack[:-1])
  return top

# Live file list built from the top fileset. 
def topFiles(pop=False):
  fileset = topFileset(pop=pop)
  if not fileset: return []
  exclude = [f[1:] for f in fileset if f[0] == '-']
  include = [f[1:] for f in fileset if f[0] == '+']
  files = []
  for f in include:
    if os.path.isfile(f[0]):
      files.append(f)
    elif os.path.isdir(f[0]):
      addDir(f, files=files, exclude=exclude)
  return files

def addDir(d, files=None, exclude=None):
  for f in os.listdir(d[0]):
    f = tuple(map(lambda x: os.path.join(x, f), d))
    if any([f[0].startswith(e[0]) for e in exclude]): continue
    if os.path.isdir(f[0]):
      addDir(f, files=files, exclude=exclude)
    else:
      files.append(f)

def popAndApplyToFileset(fn):
  files = topFiles(pop=True)
  if not files: nofiles()
  for f in files:
    (dirTree, filename) = os.path.split(f[1])
    if dirTree and not os.path.exists(dirTree): os.makedirs(dirTree)
    fn(f[0], f[1])  # fn will either be copy or move

def popAndCopyFileset(): popAndApplyToFileset(shutil.copyfile)

def popAndMoveFileset(): popAndApplyToFileset(shutil.move)

def listFiles(args):
  if args and args[0] == '--all':
    files = topFiles()
    if not files: nofiles()
    for f in files: print f[0]
    return
  fileset = topFileset()
  if not fileset: nofiles()
  for f in fileset:
    if f[0] == '+':
      print "+  %s" % f[1]
      spaces = f[1].rfind(f[2]) if f[2] != '.' else len(f[1])
      relPath = f[2] if f[2] != '.' else '*'
      print " > " + ' ' * spaces + relPath
    elif f[0] == '-':
      print "-  %s" % f[1]

def nofiles():
  print "No files"
  exit(0)

def argsAndFilelist(allargs):
  args, filelist = [], []
  takingArgs = True
  for a in allargs:
    if a.startswith('--') and takingArgs:
      if a == '--':
        takingArgs = False
      else:
        args.append(a)
    else:
      filelist.append(a)
  return args, filelist

# main
# ====

if len(sys.argv) < 2: showUsageAndExit(2)

acceptedArgs = {'ls':['--all']}

action = sys.argv[1]
args, filelist = argsAndFilelist(sys.argv[2:])
okArgs = [a in acceptedArgs.get(action, []) for a in args]
if not all(okArgs):
  print "%s is not a valid option for %s" % (args[okArgs.index(False)], action)
  exit(1)
if action == "=":
  pushNewFilelist(filelist)
elif action == "+":
  addFilelist(filelist)
elif action == "-":
  excludeFilelist(filelist)
elif action == "cp":
  popAndCopyFileset()
elif action == "mv":
  popAndMoveFileset()
elif action == "ls":
  listFiles(args)
elif action == "clearall":
  writeStack([])
else:
  print "%s not recognized" % action
  exit(1)
