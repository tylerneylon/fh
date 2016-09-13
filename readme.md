# fh

*file helper for shells*

fh, or file helper, adds to the functionality of cp and mv in bash.
If you regularly move between directories, or have multiple windows
open to various directories, fh allows you to copy/move files
between them easily.  The examples below explain its functionality.

## Installing

    git clone https://github.com/tylerneylon/fh.git
    sudo ln -s $(cd fh; pwd)/fh.py /usr/local/bin/fh

## Examples

### Copying from multiple directories

```bash
~/path/one$ fh = .  # Select all files in this directory.
~/path/one$ cd ../two
~/path/two$ fh + foo* *.png  # Also select matching files.
~/path/two$ cd ../foo
~/path/two$ fh ls  # Print out what was selected.
+  /Users/tylerneylon/path/one/ as *
+  /Users/tylerneylon/path/two/foo1 as foo1
+  /Users/tylerneylon/path/two/foo2 as foo2
+  /Users/tylerneylon/path/two/1.png as 1.png
+  /Users/tylerneylon/path/two/2.png as 2.png
~/path/foo$ fh cp  # Copy those files here.
```

When fh is given a path to a directory, it
always treats that path as the full contents of
the directory, including everything recursively.
Non-obvious file sets can be expressed using
file exclusion (the - action).

### Recursive dir copying, excluding subsets

Suppose we want to copy most of a directory over,
but not all of it:

```bash
$ fh = mydir
$ fh - mydir/.git  # Exclude the .git subdirectory.
$ cd ~/destination/
$ fh cp  # Copies over mydir less .git.
```

When you type `fh - <subpath>`, you exclude
everything in `<current dir>/<subpath>` recursively.

You can also specify custom filesets
using standard bash glob notation, as in
`fh = a* b* g* m{a,e}*`.

### Use from multiple terminal windows

Suppose you have three terminal windows open,
and execute each of these commands in a separate window:

```bash
(window 1) ~/a/b/c$ fh = file1 file2 dir1
```

```bash
(window 2) ~/d/e/f$ fh + file3 dir2 dir3
```

```bash
(window 3) ~/g/h/i$ fh mv
```

Then `file{1,2,3}` and `dir{1,2,3}` will all be moved,
including everything recursively in the directories,
to `~/g/h/i`.

## Use in bash scripts

Suppose two bash scripts both start with `fh = X`
and end with `fh [cp|mv]`.  They can still call
each other and work correctly.  In the standard
GUI cut-and-paste model, any new copied/cut selection
erases the old one, but fh keeps around a stack
of filesets, so that nested filesets (pushed via
the = action) will be remembered and act as
expected.

The stack of filesets are stored in the text file
`~/.fhstack`. If you want to reset the state of
`fh`, you can safely delete this file.

## Command overview

In general, `fh` is used like this:

    $ fh [action] [option(s)] [path/file(s)]

where `action` determines what happens.

action | what it does
-------|--------------------------------------------------------------
`=`    | push a new fileset onto fh's stack
`+`    | add files to the current fileset
`-`    | exclude files from the current fileset
`ls`   | list the current fileset
`cp`   | copy the current fileset to . and pop it from fh's stack
`mv`   | move the current fileset to . and pop it from fh's stack
`diff` | diff . with the current fileset (fileset is not popped)
