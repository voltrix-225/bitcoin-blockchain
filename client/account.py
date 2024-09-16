import sys
sys.path.append('/Users/voltr/Blockchain')

from Backend.core.EllepticCurve.EllepticCurve import Sha256Point
from Backend.util.util import hash160
from Backend.util.util import hash256 
from Backend.core.database.database import AccountDB
import secrets

class account:
    def createKeys(self):
        """Secp256k1 Curve Generator Points"""
        Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

        G = Sha256Point(Gx, Gy)

        self.privateKey = secrets.randbits(256)  #pvt key
        unCompressedPublickey = self.privateKey * G

        """ 
         # Multiply Private Key with Generator Point
         # Returns X-coordinate and Y-Coordinate 
        """
        xpoint = unCompressedPublickey.x
        ypoint = unCompressedPublickey.y

        """Address prefix for odd and even ypoints"""

        if ypoint.num % 2 == 0:
            compressKey = b'\x02' + xpoint.num.to_bytes(32, 'big')

        else:
            compressKey = b'\x03' + xpoint.num.to_bytes(32, 'big')

        """ RIPEMD160 Hashing Algorithm returns the hash of Compressed Public Key"""

        hsh160 = hash160(compressKey)

        """Prefix for Mainnet"""

        main_prefix = b'\x00'
        newAddress = main_prefix + hsh160

        """CheckSum"""

        checksum = hash256(newAddress)[:4]  #gets first 4 characters of adr
        newAddress = checksum + newAddress

        BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

        """counter to check leading zeroes"""

        count = 0
        for c in newAddress:
            if c==0:
                count += 1
            else:
                break

        """ Convert to Numeric from Bytes """

        num = int.from_bytes(newAddress, 'big')
        prefix = '1' * count

        result = ''
        
        """Convert to BASE58"""

        while num>0:
            num, mod = divmod(num, 58)
            result = result + BASE58_ALPHABET[mod]

        self.publicAddress = prefix + result

        print(f"The Private Key is {self.privateKey}")
        print(f"The Public Address is {self.publicAddress}")

if __name__ == '__main__':
    acct = account()
    acct.createKeys()
    AccountDB().write([acct.__dict__])
    
