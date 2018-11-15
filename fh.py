#!/usr/bin/python
#
# fh.py
#
# TODO Add _* functionality (destination has a flattened file structure).
# Note: I think =_ may be better than _= for the obscure reason that I
#       could then make my commands work without having to type fh first.
#       If I type _= something into the shell, it seems to interpret it
#       as setting the variable $_ (I think?).
#
# Wishlist (see also a Pages document I have):
# [ ] Be able to easily repeat the last cp/mv action.
# [ ] to undo the last action
#

"""
Usage: fh (=|+|-|cp|mv|ls|diff) [file list]

  =      push a new fileset onto fh's stack
  +      add files to the current fileset
  -      exclude files from the current fileset
  cp     copy the current fileset to . and pop it from fh's stack
  mv     move the current fileset to . and pop it from fh's stack
  ln     link the current fileset to . and pop it from fh's stack
  ls     list the current fileset
  diff   diff . and the current fileset (fileset stays active on fh's stack)

See https://github.com/tylerneylon/fh for more info.
"""

# imports
# =======

import os
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
  execName = os.path.basename(sys.argv[0])
  print __doc__.replace('fh', execName, 1)
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
  newFileset = makeFileset(filelist, '+')
  if not newFileset: print "Warning: Empty fileset created."
  stack.append(newFileset)
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

def popAndLinkFileset(): popAndApplyToFileset(os.link)

def listFiles(args):
  if args and args[0] == '--all':
    files = topFiles()
    if not files: nofiles()
    for f in files: print f[0]
    return
  printFileset(topFileset())

def printFileset(fileset, noexit=False):
  if not fileset: nofiles(noexit=noexit)
  for f in fileset:
    if f[0] == '+':
      print "+  %s" % f[1],
      relPath = f[2] if f[2] != '.' else '*'
      print "as " + relPath
    elif f[0] == '-':
      print "-  %s" % f[1]

def diffFiles():
  files = topFiles(pop=False)
  if not files: nofiles()
  for f in files:
    print('\n=== %s ===' % os.path.basename(f[1]))
    cmd = 'diff -s "%s" "%s"' % (f[1], f[0])
    os.system(cmd)

def nofiles(noexit=False):
  print "No files"
  if not noexit: exit(0)

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

# debug
# =====

def printStack(stack):
  if not stack:
    print "empty"
    return
  for fs in stack:
    printFileset(fs, noexit=True)
    print "==="


# main
# ====

if __name__ == '__main__':
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
  elif action == "ln":
    popAndLinkFileset()
  elif action == "ls":
    listFiles(args)
  elif action == "diff":
    diffFiles()
  elif action == "clearall":
    writeStack([])
  else:
    print "%s not recognized" % action
    exit(1)
