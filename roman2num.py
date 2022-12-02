# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 10:13:16 2014

@author: zzhang
"""
import pickle


class Roman2num:
    def __init__(self, fname): #file name
        self.int2roman = {}
        self.roman2int = {}
        self.fname = fname
        self.outfname = fname + '.pk'

        self.build_table()

    def build_table(self):
        """Constructs the conversion dict for int2roman and roman2int"""
        with open(self.fname, 'r') as f:
            lines = f.readlines()
            for t in lines:
                items = [x.strip() for x in t.split(':')] # ["1","I"]
                rank = int(items[0])
                roman_numeral = items[1]

                self.int2roman[rank] = roman_numeral
                self.roman2int[roman_numeral] = rank

    def write_table(self):
        """Dumps int2roman and roman2int as a pickle file"""
        with open(self.outfname, 'wb') as outf:
            pickle.dump(self.int2roman, outf)
            pickle.dump(self.roman2int, outf)
        

if __name__ == "__main__":
    r = Roman2num('roman.txt')

    import random

    for i in range(10):
        x = random.randint(0, 1000) + 1
        s = r.int2roman[x]
        print(x, s)

    r.write_table()
