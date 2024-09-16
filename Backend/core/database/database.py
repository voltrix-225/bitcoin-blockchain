import os
import json
import jsons

class BaseDB:
    def __init__(self): 
        self.filepath = 'Backend\\core\\data\\blockchain' 

    def read(self):

        if not os.path.exists(self.filepath):
            print(f"file {self.filepath} not available")

        with open(self.filepath, 'r') as file:
            raw = file.readline()
        
        if len(raw)>0:
            data = json.loads(raw)
        else:
            data = []

        return data
    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item
        
        with open(self.filepath, 'w+') as file:
            
            file.write(jsons.dumps(data))

        #HELLO LAK IN THE  MORNING. IT IS FUCKING 4:15 AM AND I AM ON THIS POS ERROR FROM THE LAST 1.5 FUCKING HOUR. THIS FUCKING DUMPS IS A MOTHERFUCKING DUMP
            
class BlockchainDB(BaseDB):
    def __init__(self):
        self.filename = 'blockchain'
        super().__init__()

    def lastBlock(self):
        data = self.read()
        if data:
            return data[-1]

class AccountDB(BaseDB):
    def __init__(self):
        self.filename = "account"
        super().__init__()
