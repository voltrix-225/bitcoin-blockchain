#users can send BTC
import time
from Backend.util.util import decode_base58
from Backend.core.script import Script
from Backend.core.transaction import TxnInput, TxnOutput, Txn
from Backend.core.database.database import AccountDB
from Backend.core.EllepticCurve.EllepticCurve import PrivateKey
class SendBTC:
    def __init__(self, fromAccount, toAccount, Amount, UTXOS):
        #UTXOS are unspent txn, keeps track of BTC balance
        self.COIN = 100000000  #in satoshis
        self.FromPublicAddress = toAccount
        self.Amount = Amount  * self.COIN
        self.utxos = UTXOS

    def scriptPublicKey(self, PublicAddress):
        '''Will return a hex public key'''
        h160 = decode_base58(PublicAddress)
        script_pubkey = Script.p2pkh_script(h160)  
        return script_pubkey

    def getPrivateKey(self):
        AllAccounts = AccountDB().read()
        for account in AllAccounts:
            if account['PublicAddress'] == self.FromPublicAddress:
                return account['privateKey']
            

    def prepareTxIn(self):
        '''Convert public address in public hash to find tx_outs that are locked to this hash '''
        TxIns = []
        self.Total = 0

        self.From_address_script_pubkey = self.scriptPublicKey(self.FromPublicAddress)
        self.fromPubKeyHash = self.From_address_script_pubkey.cmds[2]

        newutxos = {}
        try:
            while len(newutxos) < 1:
                newutxos = dict(self.utxos)
                time.sleep(2)
        except Exception as e:
            print(f"Error in converting the Managed dictionary to Normal Dictionary")


        '''Uses to send BTC in multiple txns, if single Txn not feasable'''
        for Txbyte in newutxos:
            if self.Total < self.Amount:
                TxObj = newutxos[Txbyte]
                for index, txout in enumerate(TxObj.tx_outs):
                    self.Total += txout.Amount
                    prev_tx = bytes.fromhex(TxObj.id()) 
                    TxIns.append(TxnInput(prev_tx, index))
            else:
                break

        self.isBalanceEnough = True        
        if self.Total < self.Amount:
            self.isBalanceEnough = False

        return TxIns



    def prepareTxOuts(self):
        TxOuts = []
        to_scriptPubkey = self.scriptPublicKey(self.toAccount)
        TxOuts.append(TxnOutput(self.Amount, to_scriptPubkey))   #trf to another person

        '''Mining Fees'''
        self.fee = self.COIN
        #say we have 1000 coins, and we send someone 900, the rest come back to us as change
        self.changeAmount = self.Total = self.Amount - self.fee 

        TxOuts.append(TxnOutput(self.changeAmount, self.From_address_script_pubkey))  #trf back to us
        return TxOuts

    def signTx(self):
        secret = self.getPrivateKey()
        priv = PrivateKey(secret= secret)

        for index, input in enumerate(self.TxIns):
            self.TxObj.sign_input(index, priv, self.From_address_script_pubkey)

        return True

    def prepareTransaction(self):
        self.TxIns = self.prepareTxIn()
        
        if self.isBalanceEnough:
            self.TxOuts = self.prepareTxOuts()
            self.TxObj = Txn(1, self.TxIns, self.TxOuts, 0)
            self.TxObj.TxId = self.TxObj.id()
            self.signTx()
            return self.TxObj
        
        return False