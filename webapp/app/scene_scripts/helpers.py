import sys


# EFFECTS: Loads a text file or returns an error if the file cannot be found.
def load_file(path):
    try:
        with open(path) as f:
            d = f.readlines()
            d = list(map(lambda s: s.strip(), d))
            return d
    except IOError:
        sys.exit(f"Error: file [{path}] not found. Check that the path is correct and the file exists.")
