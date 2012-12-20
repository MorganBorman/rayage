import os
import sys
import os.path

def main(args):
    sandbox_directory = os.path.abspath(args[1])
    os.chdir(sandbox_directory)
    os.execv(args[2], args[2:])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("synopsis: python " + __file__ + "foo/ foo/a.out arg1 arg2\n")
        sys.exit(os.EX_USAGE)
    sys.exit(main(sys.argv))
