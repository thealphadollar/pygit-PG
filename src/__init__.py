"""
defines helper functions to be used by all methods in the module
"""

def read_file(filename):
    """
    reads a file
    
    gives the file contents
    
    :param filename: path of the file
    :type filename: String
    """
    fh = open(filename, "r")
    try:
        return fh.read()
    except FileNotFoundError as err:
        print("File %s not found!", filename)
        print(err)
    finally:
        fh.close()

def write_file(filename, data):
    fh = open(filename, "w+")
    try:
        fh.write(data)
    except FileExistsError as err:
        print("File %s already exists!", filename)
        print(err)
    finally:
        fh.close()

