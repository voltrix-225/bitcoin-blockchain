import hashlib
from crypto.Hash import RIPEMD160
from hashlib import sha256
from math import log

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def hash160(s):
    return RIPEMD160.new(sha256(s).digest()).digest()

def bytes_needed(n):
    if n == 0:
        return 1
    else:
        return int(log(n, 256)) + 1
    
def int_to_little_endian(n, length):
    """takes int, returns little endian byte sequence"""
    return n.to_bytes(length, 'little')

def little_endian_to_int(b):
    '''takexs byte sequence, and converts to integer '''
    return int.from_bytes(b, 'little')

def decode_base58(s):
    num = 0
    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)
    
    combined = num.to_bytes(25 , byteorder='big')
    checksum = combined[-4:]

    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError(f"Bad Address {checksum}, {hash256(combined[:4][:-4])}")
    return combined[1:-4]

def encode_varint(i):
    '''encodes an int as a varint, and returns in byte'''
    if i<0xfd:                   #txn count<253(txn count is the count of lifetime txns. it is used to verify sanctity of cryto trfs in blockchain)
        return bytes([i])
    elif i<0x10000:               #254-65536 (hex of 65536 is 0x100000000)
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i<0x100000000:           
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i<0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError('Integer too large: {}'.format(i))
    

def merkle_parent_level(hashes):
    """takes list of binary hashes and returns a list half in length"""
    if len(hashes) % 2 == 1:
        hashes.append(hashes[:-1])

    parent_level = []

    for i in range(0, len(hashes), 2):
        parent = hash256(hashes[i] + hashes[i+1])
        parent_level.append(parent)

    return parent_level
    

def merkle_root(hashes):
    """takesd a list of ninary hashes and returns merkle root"""
    current_level = hashes

    while len(current_level) > 1:
        current_level = merkle_parent_level(current_level)

    return current_level[0]

def target_to_bits(target):
    """Turns a target int into bits"""
    raw_bytes = target.to_bytes(32, 'big')
    raw_bytes = raw_bytes.lstrip(b'\x00') #<1>
    if raw_bytes[0] > 0x7f:  #<2>
        exponent = len(raw_bytes) + 1
        coefficient = b'\x00' + raw_bytes[:2]
    else:
        exponent = len(raw_bytes)   #<3>
        coefficient = raw_bytes[:3]  #<4>
    new_bits = coefficient[::1] + bytes([exponent])  #<5>
    return new_bits
