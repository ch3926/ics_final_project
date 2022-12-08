"""
@author: ash
"""

import random 
from random import randint as rd
import string

class Cipher:
    def __init__(self):
        self.codebook = self.generate_codebook()
    
    def generate_codebook(self):
        random.seed("Caesar")
        codebook = []
        for e in string.ascii_letters:
            codebook.append(e)
        random.shuffle(codebook)
        return codebook
    
    def caesar_encrypt(self, message, shift):
        encrypted = ""
        for c in message:
            if c.isalpha():
                idx = self.codebook.index(c)
                e_c = self.codebook[(idx+shift)%len(self.codebook)]
                encrypted += e_c
            else: 
                encrypted += c
        return encrypted

    def caesar_decrypt(self, message, shift):
        decrypted = ""
        for c in message:
            if c.isalpha():
                idx = self.codebook.index(c)
                e_c = self.codebook[(idx-shift)%len(self.codebook)]
                decrypted += e_c
            else: 
                decrypted += c
        return decrypted


class Encryption:
    def __init__(self, num, base, mod):
        self.private = num
        self.m = mod
        self.public_base = base
        self.ppn = (self.public_base ** self.private) % self.m
        self.peer_ppn = 0
        self.key = 0
    
    def get_key(self):
        self.key = (self.peer_ppn ** self.private) % self.m
        print("key: " + str(self.key))
        return self.key

    def set_peer_ppn(self, peer_ppn):
        self.peer_ppn = peer_ppn

    def get_ppn(self):
        return self.ppn
    
    def get_num(self):
        return self.private


if __name__ == "__main__":
    # num_1 = rd(1,26)
    # num_2 = rd(1,26)
    m = 11
    base = 2

    # print("arnold num: " + str(num_1))
    # print("eve num: " + str(num_2))
    print("m: " + str(m))
    print("base: " + str(base))
    
    arnold = Encryption(2, m, base)
    arnold_ppn = arnold.get_ppn()
    eve = Encryption(3, m, base)
    eve_ppn = eve.get_ppn()

    print("arnold num: " + str(arnold.get_num()))
    print("eve num: " + str(eve.get_num()))

    print("arnold ppn: " + str(arnold_ppn))
    print("eve ppn: " + str(eve_ppn))

    arnold.set_peer_ppn(eve_ppn)
    eve.set_peer_ppn(arnold_ppn)

    if arnold.get_key() == eve.get_key():
        print("yayyy")
    else:
        print("noooo")

    # Hello Kitty
    m = "Hello Kitty!"
    shift = 3
    c = Cipher()
    encoded = c.caesar_encrypt(m, shift)
    decoded = c.caesar_decrypt(encoded, shift)
    print("Origin:", m)
    print("Encoded:", encoded)
    print("Decoded:", decoded)

    # I love ICS!!!
    m = "I love ICS!!!"
    shift = 3
    c = Cipher()
    encoded = c.caesar_encrypt(m, shift)
    decoded = c.caesar_decrypt(encoded, shift)
    print("Origin:", m)
    print("Encoded:", encoded)
    print("Decoded:", decoded)

# python package for public private keys