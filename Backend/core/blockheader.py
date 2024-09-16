from Backend.util.util import hash256, int_to_little_endian, little_endian_to_int

class Blockheader:
    def __init__ (self, version, prev_hash, merkleroot, timestamp, bits):
        self.version = version
        self.prev_hash = prev_hash
        self.merkleroot = merkleroot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockhash = " "

    def mine(self, target):
        self.blockHash = target + 1

        while self.blockHash > target:
            self.blockHash = little_endian_to_int(
                hash256(
                    int_to_little_endian(self.version, 4)
                    + bytes.fromhex(self.prev_hash)[::-1]
                    + bytes.fromhex(self.merkleroot)
                    + int_to_little_endian(self.timestamp, 4)
                    + self.bits
                    + int_to_little_endian(self.nonce, 4)
                )
            )
            self.nonce += 1
            print(f"Mining Started {self.nonce}", end="\r")
        self.blockHash = int_to_little_endian(self.blockHash, 32).hex()[::-1]
        self.bits = self.bits.hex()