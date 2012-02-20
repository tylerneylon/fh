#!/usr/bin/python
#
# fh.py
#
"""
Usage: fh [_](=|+|-|cp|mv|ls) [file list]
"""

# TODO
# * Disallow ".." as a dirname in any given file, unless it's added flattened.
#   Because that doesn't fit the purpose of fh, plus it will confuse os.makedirs.

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

# TODO rename this mofo
# prepend every string with a character
def preChar(paths, ch):
  return map(pathEntry(ch), paths)
  #return [ch + os.path.abspath(p) for p in paths]

def pathEntry(ch):
  return lambda p: (ch, os.path.abspath(p), p)

def pushNewFileset(fileset):
  stack = readStack()
  stack.insert(0, preChar(fileset, '+'))
  writeStack(stack)

def addFileset(fileset):
  stack = readStack()
  if not stack:
    pushNewFileset(fileset)
    return
  stack[-1] += preChar(fileset, '+')
  writeStack(stack)

def excludeFileset(fileset):
  stack = readStack()
  if not stack:
    # TODO
    raise Exception('ruh roh')
  stack[-1] += preChar(fileset, '-')
  writeStack(stack)

# Same format as user input. 
def topFileset(pop=False):
  stack = readStack()
  return stack[-1] if stack else None

# Live file list built from the top fileset. 
def topFiles(pop=False):
  fileset = topFileset(pop=pop)
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
    f = tuple(map(lambda x: x + os.sep + f, d))
    if any([f[0].startswith(e[0]) for e in exclude]): continue
    if os.path.isdir(f[0]):
      addDir(f, files=files, exclude=exclude)
    else:
      files.append(f)

def popAndCopyFileset():
  files = topFiles(pop=True)
  for f in files:
    (dirTree, filename) = os.path.split(f[1])
    if dirTree and not os.path.exists(dirTree): os.makedirs(dirTree)
    shutil.copyfile(f[0], f[1])

def popAndMoveFileset():
  pass

def showFileset():
  pass

# main
# ====

if len(sys.argv) < 2: showUsageAndExit(2)

actionStr = sys.argv[1]
fileset = sys.argv[2:]
if actionStr == "=":
  pushNewFileset(fileset)
elif actionStr == "+":
  addFileset(fileset)
elif actionStr == "-":
  excludeFileset(fileset)
elif actionStr == "cp":
  popAndCopyFileset()
elif actionStr == "mv":
  popAndMoveFileset()
elif actionStr == "ls":
  showFileset()

