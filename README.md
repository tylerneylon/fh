fh, or file helper, adds to the functionality of cp and mv in bash.
If you regularly move between directories, or have multiple windows
open to various directories, fh allows you to copy/move files
between them easily.  The examples below explain its functionality.

# Installing

    $ git clone git@github.com:tylerneylon/fh.git
    $ sudo ls -s fh/fh.py /usr/local/bin/fh

# Examples

## Copying from multiple directories

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

(todo: fill out other examples)

## Recursive dir copying, excluding subsets

## Use from multiple terminal windows

## Use in bash scripts

# Command overview

In general, `fh` is used like this:

    $ fh [action] [option(s)] [path/file(s)]

where `action` determines what happens.

<table>
  <tr>
    <td> = </td>
    <td> push a new fileset onto fh's stack </td>
  </tr>
  <tr>
    <td> + </td>
    <td> add files to the current fileset </td>
  </tr>
  <tr>
    <td> - </td>
    <td> exclude files from the current fileset </td>
  </tr>
  <tr>
    <td> cp </td>
    <td> copy the current fileset to . and pop it from fh's stack </td>
  </tr>
  <tr>
    <td> mv </td>
    <td> move the current fileset to . and pop it from fh's stack </td>
  </tr>
  <tr>
    <td> ls </td>
    <td> list the current fileset </td>
  </tr>
</table>
