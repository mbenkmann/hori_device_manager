#!/bin/python
'''
USAGE: isolate <f> ... =  <f> ... != <f> ... = <f>... != <f> ...

Each <f> is a file containing a memory dump as produced by hori.py hexdump.
Files are processed in sequence. Each file is compared with the previous file.
If the most recent operator on the command line was "=" (the default as long
as no other operator overrides it), then all offsets are eliminated from
consideration where the files differ. If the most recent operator was "!=", then
all offsets are eliminated from consideration where the files are equal.
After the last file, the program lists all remaining offsets with the values
they had in all the files.
'''
import sys


def compare(op, data1, data2):
    for i, d in enumerate(data1):
        if d == -1 or (op == "=" and d != data2[i]) or (op == "!=" and d == data2[i]):
            data2[i] = -1


if __name__ == "__main__":
    op = "="
    files = []
    for arg in sys.argv[1:]:
        if arg == "=" or arg == "==":
            op = "="
        elif arg == "!=":
            op = "!="
        else:
            with open(arg) as f:
                data = [int(x, 16) for x in f.read(-1).split()]
                if len(files) > 0:
                    compare(op, files[-1], data)
                files.append(data)

    if len(files) > 1:
        data = files[-1]
        for i, d in enumerate(data):
            if d >= 0:
                sys.stdout.write("{:04x} ".format(i))
                for f in files:
                    sys.stdout.write("{:02x} ".format(f[i]))
                sys.stdout.write("\n")
