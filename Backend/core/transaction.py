from Backend.core.script import Script
from Backend.util.util import hash256,int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int, encode_varint

ZERO_HASH = b'\0' * 32
REWARD = 50
PRIVATE_KEY = (
    "59024195091230105596801455306913435815673319996141880726735464739248197324364"
)
MINER_ADDRESS = "1LYgXwYXw16GJXgDwHV7aCNijnQWYEdc1C"
SIGHASH_ALL = 1

  
class CoinbaseTx:
    def __init__(self, BlockHeight):
        self.BlockHeightInLittleEndian = int_to_little_endian(BlockHeight, bytes_needed(BlockHeight))

    def coinbaseTransaction(self):
        prev_txn = ZERO_HASH
        prev_index = 0xffffffff
        txn_ins = []
        txn_ins.append(TxnInput(prev_txn, prev_index))
        txn_ins[0].script_sign.cmds.append(self.BlockHeightInLittleEndian)

        txn_outs = []
        target_amount = REWARD * 50
        targeth_160 = decode_base58(MINER_ADDRESS)

        target_script = Script.p2pkh_script(targeth_160)
        txn_outs.append(TxnOutput(amount = target_amount, script_publicKey= target_script))

        coinBaseTx = Txn(1, txn_ins, txn_outs, 0)
        coinBaseTx.TxId = coinBaseTx.id()

        return coinBaseTx
        



class Txn:
    def __init__(self, version, txn_ins, txn_outs, locktime):
        self.version = version
        self.txn_ins = txn_ins
        self.txn_outs = txn_outs
        self.locktime = locktime

    def id(self):
        '''Human readable Transaction ID'''
        return self.hash().hex()

    def hash(self):
        '''binary hash of serialization, reversed as per btc standards: this is the transaction ID'''
        return hash256(self.serialize())[::-1]


    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.txn_ins))

        for txn_in in self.txn_ins:
            result += txn_in.serialize()
        
        result += encode_varint(len(self.txn_outs))
        
        for txn_out in self.txn_outs:
            result += txn_out.serialize()

        
        result += int_to_little_endian(self.locktime, 4)

        return result
    
    
    def sign_input(self, input_index, private_key, script_pubkey):
        z = self.sigh_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, "big")
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = Script([sig, sec])

    def verify_input(self, input_index, script_pubkey):
        tx_in = self.tx_ins[input_index]
        z = self.sigh_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)

    def sigh_hash(self, input_index, script_pubkey):
        '''Hash of the signature'''
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.txn_ins))

        for i, tx_in in enumerate(self.txn_ins):
            if i == input_index:
                s += TxnInput(tx_in.prev_txn, tx_in.prev_index, script_pubkey).serialize()
            else:
                s += TxnInput(tx_in.prev_txn, tx_in.prev_index).serialize()
            
            s += encode_varint(len(self.txn_outs))
            
            for tx_out in self.tx_outs:
                s += tx_out.serialize()

            s += int_to_little_endian(self.locktime, 4)
            s += int_to_little_endian(SIGHASH_ALL, 4)

            h256 = hash256(s)

            return int.from_bytes(h256, 'big')

    def sign_input(self, input_index, private_key, script_pubkey):
        z = self.sigh_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, 'big')
        sec = private_key.point.sec()
        self.txn_ins[input_index].script_sig = Script([sig, sec])

    

    def verify_input(self, input_index, script_pubkey):
        tx_in = self.txn_ins[input_index]
        z = self.sigh_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)


    def is_Coinbase(self):
        """
        #check that there is exactly 1 inp
        # grab the first inp and check id prex tx hash is b'x\00' *32
        # check thet the first input prev_index is 0xffffffff
        recognizes coinbase txn
        """

        if len(self.txn_ins) != 1:
            return False
        
        first_input = self.txn_ins[0]
        if first_input.prev_txn != b'\00' * 32:
            return False
        
        if first_input.prev_index != 0xffffffff:
            return False
        
        return True  #all conditions check, txn is coinbase


    def to_Dict(self):
        """
        Convert Transaction
         # Convert prev_tx Hash in hex from bytes
         # Convert Blockheight in hex which is stored in Script signature
         prev txn is in json, we convert to dict
        """

        for tx_index, tx_in in enumerate(self.txn_ins):
            if self.is_Coinbase():
                tx_in.script_sig.cmds[0] = little_endian_to_int(tx_in.script_sigcmds[0])

            tx_in.prev_txn = tx_in.prev_txn.hex()

            for index, cmd in enumerate(tx_in.script_sig.cmds):
                if isinstance(cmd, bytes):
                    tx_in.script_sig.cmds[index] = cmd.hex()
            tx_in.script_sig = tx_in.script_sig.__dict__
            self.txn_in[tx_index] = tx_in.__dict__


        '''Convert txn_output to dict
        # if there are numbers, we do nothing
        # conver byte values to hex
        # loop through txn_output obj and convert to dict
        '''
        for index, tx_out in enumerate(self.txn_outs):
            tx_out.script_pubkey.cmds[2] = tx_out.script_pubkey.cmds[2].hex()
            tx_out.script_pubkey = tx_out.script_pubkey.__dict__

        return self.__dict__


         
class TxnInput:
    def __init__(self, prev_txn, prev_index, script_sign = None, sequence = 0xffffffff):
        self.prev_txn = prev_txn
        self.prev_index = prev_index
        if script_sign is None:
            self.script_sign = Script()
        else:
            self.script_sign = script_sign
        self.sequence = sequence

    def serialize(self):
        result = self.prev_txn[::-1]  #reversed becoz, such is followed in btc
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sign.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result




class TxnOutput:
    def __init__(self, amount, script_publicKey):
        self.amount = amount
        self.script_publicKey = script_publicKey

    def serialize(self):
        result = int_to_little_endian(self.amount, 8)
        result += self.script_publicKey.serialize()
        return result