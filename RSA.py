from random import randint as rd
import math
import string

class RSA:
    def __init__(self):
        # pass
        self.p = self.generate_num()
        self.q = self.generate_num()
        # print(f"p: {self.p}, q: {self.q}")
        self.compute_key()
    
    def generate_num(self):
        is_prime = False
        num=0
        while not is_prime:
            num = rd(10,50)
            is_prime = self.is_prime(num)
        return num
    
    def is_prime(self, n: int) -> bool:
        if n <= 3:
            return n > 1
        if n % 2 == 0 or n % 3 == 0:
            return False
        limit = int(n**0.5)
        for i in range(5, limit+1, 6):
            if n % i == 0 or n % (i+2) == 0:
                return False
        return True

    def get_d(self):
        return self.d
    
    def compute_key(self):
        self.n = self.p * self.q
        self.lcm = math.lcm(self.p-1, self.q-1)
        is_prime = False
        while not is_prime:
            self.e = rd(2,self.lcm-1)
            is_prime = self.is_prime(self.e)
        self.d = self.e * self.lcm + 1
        print(f"n: {self.n}, e: {self.e}")
    
    # ***public key***
    def get_n_e(self):
        return self.n, self.e

class Cipher:
    def __init__(self):
        self.alpha2num = {}
        self.num2alpha = {}
        counter = 0
        for letter in string.ascii_letters:
            self.alpha2num[letter] = counter
            self.num2alpha[counter] = letter
            counter += 1
    
    def encode(self, m, shift):
        shift = str(shift)
        #print(f"str: {shift[0:2]}")
        #print(f"int: {int(shift[0:2])}")
        msg = ""
        while len(shift) < len(m):
            shift += shift
        if len(shift) > len(m):
            shift = shift[:len(m)]
        for idx in range(len(m)):
            #print(f"idx: {idx}")
            # new letter = old letter + key letter
            if m[idx].isalpha():
                old_letter_idx = self.alpha2num[m[idx]]
                #print(shift[idx] + shift[idx+1])
                cb_shift = int(shift[idx:idx+2]) % 52 # returns a number
                new_letter_idx = old_letter_idx + cb_shift
                # new_letter = self.num2alpha[m[idx] + cb_shift]
                new_letter = self.num2alpha[new_letter_idx % 52]
                msg+=new_letter
            else:
                msg+=m[idx]

        return msg


    def decode(self, m, shift):
        shift = str(shift)
        msg = ""
        while len(shift) < len(m):
            shift += shift
        if len(shift) > len(m):
            shift = shift[:len(m)]
        for idx in range(len(m)):
            #print(f"idx: {idx}")
            # new letter = old letter + key letter
            if m[idx].isalpha():
                old_letter_idx = self.alpha2num[m[idx]]
                #print(shift[idx] + shift[idx+1])
                cb_shift = int(shift[idx:idx+2]) % 52 # returns a number
                new_letter_idx = old_letter_idx - cb_shift
                # new_letter = self.num2alpha[m[idx] + cb_shift]
                new_letter = self.num2alpha[new_letter_idx % 52]
                msg+=new_letter
            else:
                msg+=m[idx]
        return msg
if __name__ == "__main__":
    arnold = RSA()
    arnold_d = arnold.get_d()
    arnold_n, arnold_e = arnold.get_n_e()
    print("-----arnold-----")
    print(f"d: {arnold_d}, n: {arnold_n}, e: {arnold_e}")
    
    eve_m = rd(1,10)
    eve_c = eve_m ** arnold_e % arnold_n
    print("-----eve-----")
    print(f"m: {eve_m}, c: {eve_c}")

    print("case 1: eve sends a message")
    arnold_m = eve_c ** arnold_d % arnold_n
    eve_msg1 = "Hello Kitty!"
    cipher = Cipher()
    encoded = cipher.encode(eve_msg1, eve_c)
    print(f"eve_c: {eve_c}, arnold_m {arnold_m}")
    decoded = cipher.decode(encoded, arnold_m)
    print("Origin:", eve_msg1)
    print("Encoded:", encoded)
    print("Decoded:", decoded)

    print("------------------------")
    arnold = RSA()
    arnold_d = arnold.get_d()
    arnold_n, arnold_e = arnold.get_n_e()
    print("-----arnold-----")
    print(f"d: {arnold_d}, n: {arnold_n}, e: {arnold_e}")
    
    eve_m = rd(1,10)
    eve_c = eve_m ** arnold_e % arnold_n
    print("-----eve-----")
    print(f"m: {eve_m}, c: {eve_c}")

    print("case 2: arnold sends a message")
    arnold_m = eve_c ** arnold_d % arnold_n
    arnold_msg1 = "I Love ICS!"
    cipher = Cipher()
    encoded = cipher.encode(arnold_msg1, arnold_m)
    print(f"eve_c: {eve_c}, arnold_m: {arnold_m}")
    decoded = cipher.decode(encoded, eve_c)
    print("Origin:", arnold_msg1)
    print("Encoded:", encoded)
    print("Decoded:", decoded)