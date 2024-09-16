class Block:
    def __init__(self, block_height, block_size, block_header, txn_count, txn):
        self.block_height = block_height
        self.block_size = block_size
        self.block_header = block_header
        self.txn_count = txn_count
        self.txn = txn 

    