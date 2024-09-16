import sys
sys.path.append('\\Users\\voltr\\Blockchain')

#Backend\core\block.py
from Backend.core.block import Block
from Backend.core.blockheader import Blockheader
from Backend.util.util import hash256, merkle_root, target_to_bits
from Backend.core.database.database import BlockchainDB
from Backend.core.transaction import CoinbaseTx
from Frontend.run import main
from multiprocessing import Process, Manager

import time


ZERO_HASH = '0' * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000

class Blockchain:
    def __init__(self, utxos, Mempool):
        self.utxos = utxos
        self.MemPool = MemPool
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)
         

    def write_on_disk(self, block):
        blockchainDB = BlockchainDB()
        blockchainDB.write(block)

    def fetch_last_block(self):
        blockchainDB = BlockchainDB()
        return blockchainDB.lastBlock()
    
    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.addBlock(BlockHeight, prevBlockHash)

    def store_utxos_in_cache(self):
        """Keep track of unspent txns in cache memory for fast retrival"""
        for tx in self.addTransactionInBlock:
            print(f"Transaction Added {tx.TxId}")
            self.utxos[tx.TxId] = tx

    def remove_Spent_Transactions(self):
        for txId_index in self.remove_spent_transactions:
            if txId_index[0].hex() in self.utxos:
                if len(self.utxos[txId_index.hex()].tx_outs) < 2:
                    print(f"Spent transaction Removed {txId_index[0].hex()}")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prev_transaction = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prev_transaction.tx_outs.pop(txId_index[1])
    
    def read_transaction_from_memorypool(self):
        """read txns from mempool"""
        self.TxIds = []
        self.addTransactionInBlock = []
        self.remove_spent_transactions = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionInBlock.append(self.MemPool[tx])

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_txn, spent.prev_index])


    def remove_transactions_from_memorypool(self):
        """remove transactions from memory pool"""
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]


    def convert_to_json(self):
        self.TxJson = []
        for tx in self.addTransactionInBlock:
            self.TxJson.append(tx.to_dict())

    def calculate_fee(self):
        self.input_amount = 0
        self.output_amount = 0
        """calc input amt"""
        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount

        """calc output amt"""
        for tx in self.addTransactionInBlock:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount
        self.fee = self.input_amount - self.output_amount


    def addBlock(self, BlockHeight, prevBlockHash):
        self.read_transaction_from_memorypool()
        self.calculate_fee()
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.coinbaseTransaction() 

        coinbaseTx.txn_outs[0].amount = coinbaseTx.txn_outs[0].amount + self.fee

        self.TxIds.insert(0, bytes.fromhex(coinbaseTx.id()))
        self.addTransactionInBlock.insert(0, coinbaseTx)

        merkelroot = merkle_root(self.TxIds)[::-1].hex( )
    
        blockheader = Blockheader(VERSION, prevBlockHash, merkelroot, timestamp, self.bits)

        blockheader.mine(self.current_target)
        self.remove_Spent_Transactions()
        self.read_transaction_from_memorypool()
        self.store_utxos_in_cache()
        self.convert_to_json()

        print(f"Block {BlockHeight} mined, with Nonce Value of {blockheader.nonce}")
        self.write_on_disk(
            [
                Block(
                    BlockHeight, self.Blocksize, blockheader.__dict__, 1, self.TxJson
                ).__dict__
            ]
        )

    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()

        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock['block_height'] + 1
            prevBlockHash = lastBlock['block_header']['blockhash']

            self.addBlock(BlockHeight, prevBlockHash)


if __name__ == '__main__':
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()

        webapp = Process(target = main, args = (utxos,MemPool))
        webapp.start()

        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()

    