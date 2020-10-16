"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
MUL = 0b10100010
ADD = 0b10100000
DIV = 0b10100011
SUB = 0b10100001
JMP = 0b01010100
JNE = 0b01010110
CMP = 0b10100111
JEQ = 0b01010101
SP = 7

class CPU:
    def __init__(self):
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[7] = 0xF4
        self.pc = 0
        self.halted = False
        self.flg = 0b00000000

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, val):
        self.ram[address] = val

    def load(self, filename):
        """Load a program into memory."""
        address = 0
        
        with open(filename) as f:
            for line in f:
                line_split = line.split('#')
                val = line_split[0].strip()
                if val == '':
                    continue

                val = int(val, 2)
                self.ram_write(address, val)
                address +=1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] /= self.reg[reg_b]
            else:
                raise Exception("Cannot divide by 0")
        elif op == "CMP":
            operand_a = self.reg[reg_a]
            operand_b = self.reg[reg_b]
            if operand_a == operand_b:
                self.flg = 0b00000001
            elif operand_a < operand_b:
                self.flg = 0b00000100
            elif operand_a > operand_b:
                self.flg = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.halted:
            instruction = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if instruction == HLT:
                self.halted = True
                self.pc += 1
            elif instruction == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == PUSH:
                self.reg[SP] -= 1
                get_val = self.reg[operand_a]
                self.ram_write(self.reg[SP], get_val)
                self.pc +=2
            elif instruction == POP:
                top_val = self.ram_read(self.reg[SP])
                self.reg[operand_a] = top_val
                self.reg[SP] +=1
                self.pc += 2
            elif instruction == CALL:
                value = self.pc + 2
                self.reg[SP] -= 1
                self.ram_write(self.reg[SP], value)
                self.pc = self.reg[operand_a]
            elif instruction == RET:
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1
            elif instruction == ADD:
                self.reg[operand_a] += self.reg[operand_b]
                self.pc += 3
            elif instruction == MUL:
                self.reg[operand_a] *= self.reg[operand_b]
                self.pc += 3
            elif instruction == JMP:
                self.pc = self.reg[operand_a]
            elif instruction == JEQ:
                if self.flg & 0b1 == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc +=2
            elif instruction == JNE:
                if self.flg & 0b1 == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc +=2
            elif instruction == CMP:
                self.alu('CMP', operand_a, operand_b)
                self.pc += 3
            else:
                print("Invalid instruction")