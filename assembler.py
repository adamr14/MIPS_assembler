# Adam Rankin
# ECE 2500
# Project 1 - MIPS assembler
#
#
# The goal of this project is to implement a MIPS instruction set assembler. Both I and R type instructions
# will be accounted for. The input will come from a file called *.s, and the output will be in a file
# called *.obj
#
#
#


#
# Assember class object to hold relevant structures and methods
#
class assembler():
    #
    # assembler constructor (used to set up dictionaries of instructions and registers)
    #
    def __init__(self, filename):
        self.inputFilename = filename
        if len(filename.split('.s')) < 2:
            raise Exception("Invalid Filename: Filename must end in '.s'")
        else:
            self.outputFilename = filename.split('.s')[0] + '.obj'
            self.instructions = self.__build_instruction_dict()
            self.registers = self.__build_register_dict()
            self.labels = {} # label map
            self.content = [] #list of all the lines in input file
            self.output = [] #list of all lines in output file
            self.num_labels = 0 #number of labels

    #
    # Reads and pre-processes all instructions for whitespace
    #
    def read_file(self):
        with open(self.inputFilename, 'r') as assembly_file:
            self.content = assembly_file.readlines()
        self.content = [x.strip() for x in self.content]
        self.content = [x.replace('\t', ' ') for x in self.content]
        assembly_file.close()
        return

    #
    # Parses all instructions by type (see __i_type and __j_type)
    #
    def parse(self):
        self.__map_labels()
        line_num = 1
        for line in self.content:
            instruction = line.split(' ')[0]
            if instruction  in self.instructions.keys():
                type = self.instructions[instruction]['format']
            else:
                raise Exception("Cannot Assemble '" + line + "' at line number: " + str(line_num) + " (ignoring labels)")
            if instruction == 'jr':
                try:
                    self.output.append(self.__jr(line))
                except:
                    raise Exception("Cannot Assemble '" + line +"' at line number: " + str(line_num)+ " (ignoring labels)")
            elif type == 'I':
                try:
                    self.output.append(self.__i_type(line, line_num))
                except:
                    raise Exception("Cannot Assemble '" + line +"' at line number: " + str(line_num)+ " (ignoring labels)")
            else:
                try:
                    self.output.append(self.__r_type(line, line_num))
                except:
                    raise Exception("Cannot Assemble '" + line + "' at line number: " + str(line_num)+ " (ignoring labels)")
            line_num += 1
        return

    #
    # writes output to file
    #
    def write_output(self):
        with open (self.outputFilename, 'w') as output_file:
            for line in self.output:
                output_file.write("%s\n" % line)
        output_file.close()
        return

    #
    # Private functions
    #

    #
    # Maps labels before instructions are read, Keeps track of line number for each label, removes labels from input
    #
    def __map_labels(self):
        line_num = 0
        for line in self.content:
            if line.endswith(':'):
                self.labels[line.strip(':')] = line_num + self.num_labels
                self.num_labels += 1
                self.content.remove(line)
            line_num += 1
        return

    #
    # Parses an i-type instruction
    #
    def __i_type(self, line='', num=0):
        # If pointer notation used ( only 2 args)
        if len(line.split(' ')) == 3:
            instruction = line.split(' ')[0]
            rt = line.split(' ')[1].strip(',')
            pointer = line.split(' ')[2]
            i = int(pointer.split('(')[0])
            rs = pointer.split('(')[1].split(')')[0]
        else:
            #print (line)
            instruction = line.split(' ')[0]
            # Check for branch instructions
            if instruction=='bne' or instruction=='beq':
                rs = line.split(' ')[1].strip(',')
                rt = line.split(' ')[2].strip(',')
            else:
                rt = line.split(' ')[1].strip(',')
                rs = line.split(' ')[2].strip(',')
            imm = line.split(' ')[3]
            #calculate immediate
            if imm in self.labels.keys():
                i = self.__calculate_branch(imm, num)
            else:
                i = int(imm)
        #buld instructions in binary
        bin_instr = self.instructions[instruction]['code']
        bin_instr += self.registers[rs]
        bin_instr += self.registers[rt]
        #build immediate string (sign extend if negative)
        if i < 0:
            bin_imm = bin(i & 0xffff).split('0b')[1]
        else:
            bin_imm = bin(i).split('0b')[1].zfill(16)
        bin_instr += bin_imm
        return hex(int(bin_instr, 2)).split('0x')[1].zfill(8)

    #
    # Take in an R-Type instruction, output hex string
    #
    def __r_type(self, line='', num=0):
        instruction = line.split(' ')[0]
        rd = line.split(' ')[1].strip(',')
        rs = line.split(' ')[2].strip(',')
        rt = line.split(' ')[3]
        bin_instr = '000000'
        #if rt is a register
        if rt in self.registers.keys():
            bin_instr += self.registers[rs]
            bin_instr += self.registers[rt]
            bin_instr += self.registers[rd]
            bin_instr += '00000'
        #if there is a shift amount
        else:
            shamt = int(rt)
            bin_instr += '00000'
            bin_instr += self.registers[rs]
            bin_instr += self.registers[rd]
            bin_instr += "{0:b}".format(shamt).zfill(5)
        bin_instr += self.instructions[instruction]['code']
        return hex(int(bin_instr, 2)).split('0x')[1].zfill(8)


    #
    # jr
    #
    def __jr(self, line=''):
        rs = line.split(' ')[1].strip(',')
        bin_instr = '000000' + self.registers[rs]
        bin_instr += '000000000000000'
        bin_instr += self.instructions['jr']['code']
        return hex(int(bin_instr, 2)).split('0x')[1].zfill(8)

    #
    # Calculates branches
    #
    def __calculate_branch(self, label='', line_num=0):
        line_num += 1; # PC = PC+4
        branch = self.labels[label] - line_num
        return branch if branch >= 0 else branch+1

    #
    # Set up instruction dictionary
    #
    def __build_instruction_dict(self):
        instructions = dict()
        instructions['add'] = {'format': 'R',
                               'code': '100000'}
        instructions['addi'] = {'format': 'I',
                                'code': '001000'}
        instructions['addiu'] = {'format': 'I',
                                 'opcode': '001001'}
        instructions['and'] = {'format': 'R',
                               'code': '100100'}
        instructions['addu'] = {'format': 'R',
                                'code': '100001'}
        instructions['andi'] = {'format': 'I',
                                'code': '001100'}
        instructions['beq'] = {'format': 'I',
                               'code': '000100'}
        instructions['bne'] = {'format': 'I',
                               'code': '000101'}
        instructions['jr'] = {'format': 'R',
                              'code': '001000'}
        instructions['lbu'] = {'format': 'I',
                               'code': '100100'}
        instructions['lhu'] = {'format': 'I',
                               'code': '100100'}
        instructions['ll'] = {'format': 'I',
                              'code': '100101'}
        instructions['lui'] = {'format': 'I',
                               'code': '001111'}
        instructions['lw'] = {'format': 'I',
                              'code': '100011'}
        instructions['nor'] = {'format': 'R',
                               'code': '100111'}
        instructions['or'] = {'format': 'R',
                              'code': '100101'}
        instructions['ori'] = {'format': 'I',
                               'code': '001101'}
        instructions['slt'] = {'format': 'R',
                               'code': '101010'}
        instructions['slti'] = {'format': 'I',
                                'code': '001010'}
        instructions['sltiu'] = {'format': 'I',
                                 'code': '001011'}
        instructions['sltu'] = {'format': 'R',
                                'code': '101011'}
        instructions['sll'] = {'format': 'R',
                               'code': '000000'}
        instructions['srl'] = {'format': 'R',
                               'code': '000010'}
        instructions['sb'] = {'format': 'I',
                              'code': '101000'}
        instructions['sc'] = {'format': 'I',
                              'code': '111000'}
        instructions['sh'] = {'format': 'I',
                              'code': '101001'}
        instructions['sw'] = {'format': 'I',
                              'code': '101011'}
        instructions['sub'] = {'format': 'R',
                               'code': '100010'}
        instructions['subu'] = {'format': 'R',
                                'code': '100011'}
        return instructions

    #
    # Set up register dictionary
    #
    def __build_register_dict(self):
        registers = dict()
        registers['$zero'] = '00000'
        registers['$at'] = '00001'
        registers['$v0'] = '00010'
        registers['$v1'] = '00011'
        registers['$a0'] = '00100'
        registers['$a1'] = '00101'
        registers['$a2'] = '00110'
        registers['$a3'] = '00111'
        registers['$t0'] = '01000'
        registers['$t1'] = '01001'
        registers['$t2'] = '01010'
        registers['$t3'] = '01011'
        registers['$t4'] = '01100'
        registers['$t5'] = '01101'
        registers['$t6'] = '01110'
        registers['$t7'] = '01111'
        registers['$s0'] = '10000'
        registers['$s1'] = '10001'
        registers['$s2'] = '10010'
        registers['$s3'] = '10011'
        registers['$s4'] = '10100'
        registers['$s5'] = '10101'
        registers['$s6'] = '10110'
        registers['$s7'] = '10111'
        registers['$t8'] = '11000'
        registers['$t9'] = '11001'
        registers['$k0'] = '11010'
        registers['$k1'] = '11011'
        registers['$gp'] = '11100'
        registers['$sp'] = '11101'
        registers['$fp'] = '11110'
        registers['$ra'] = '11111'
        return registers
