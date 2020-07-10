import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from flask import Flask, jsonify, request
from textwrap import dedent


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100) #Genezis block


    def new_block(self, proof, previous_hash=None,):
        '''Create a new block'''

        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = [] #Reset current transaction list

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        '''Create a new transaction'''

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return  self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        '''Create SHA-256 block hash'''

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        '''Return a last block in chain'''

        return self.chain[-1]

    def proof_of_woork(self, last_proof: int):
        '''
        My PoW Algorithm:
        Find a p'
        hash(pp') must contains 4 lead 0, where p - is previous p'
        p - last proof
        p' - new proof
        :param last_proof: <int>
        :return: <int>
        '''

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int):
        '''
        Check the Proof - are the hash(last_proof, proof) contains 0000
        :param last_proof <int>:
        :param proof: <int>
        :return: <bool>
        '''

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


#Flask rest-interface

app = Flask(__name__)

#Create a unic global adress to this node

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    #Starting PoW alg
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_woork(last_proof)

    #We should get a reward
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    block = blockchain.new_block(proof)

    response = {
        'message': "Hello, i'am CorrectionClassCoin block ( ͡⊙ ͜ʖ ͡⊙)",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    #Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'transaction will be added to Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    responce = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return  jsonify(responce), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)




