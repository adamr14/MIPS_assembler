
#imports
import sys
from assembler import assembler

# main function
def main():
    #checks for valid args
    if len(sys.argv) != 2:
        print("Error: Invalid Arguments")
    else:
        a = assembler(sys.argv[1])
        a.read_file()
        a.parse()
        a.write_output()

if __name__=='__main__':
    main()