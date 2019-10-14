Instructions for use:
1. myAssembler.py and assembler.py must be in the same directory
	a. myAssembler holds the main function
	b. assembler holds the assembler class and all functions
	
2. Any input file must end in '.s' and be called in relation to the directory of myAssembler

3. Per the project spec, the assembler can be called from the command line as follows 'myAssmbler *.s'
	a. If python is installed 'python3 myAssembler.py *.s may work as well
	b. if using windows powershell '.\myAssembler.py test_cases/test_case3.s' works but no errors will be output
	
4. The outputfile, assuming to errors have occured, will be named the same as the input, in the same directory with a '.obj' extension