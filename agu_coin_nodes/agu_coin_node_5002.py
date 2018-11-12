#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modele 1 - Create BlockChain

"""
Created on Sun Nov 12 17:38:13 2018

@author: mmuazekici
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
import time


# Part 1 - Building BlockChain

class Blockchain:

    difficulty = 4
    leading_zeros = '0000'

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.chain.append(self.create_block(previous_hash='0'))
        self.chain[0]['hash'] = self.proof_of_work(self.chain[0])
        self.nodes = set()

    def create_block(self, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': '',
                 'nonce': 0,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions,
                 'hash': ""}
        self.transactions = []
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        new_nonce = 1
        check_proof = False
        while check_proof is False:
            block['nonce'] = new_nonce
            block['timestamp'] = str(datetime.datetime.now())
            encoded_block = json.dumps(block, sort_keys=True).encode()
            block_hash = hashlib.sha256(encoded_block).hexdigest()
            if block_hash[:self.difficulty] == self.leading_zeros:
                check_proof = True
            else:
                new_nonce += 1
        return block_hash

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        current_block_index = 1
        while current_block_index < len(chain):
            current_block = chain[current_block_index]
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            block_hash = current_block['hash']
            if block_hash[:self.difficulty] != self.leading_zeros:
                return False
            previous_block = current_block
            current_block_index += 1
        return True

    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False



# Part 2 - Mining BlockChain
# Create a Web App
app = Flask(__name__)

#  Creating an address for the node on Port 5002
node_address = str(uuid4()).replace('-', '')

# Create a Blockhain Instance

blockchain = Blockchain()


# Mining a new block

@app.route('/mine_block', methods=['GET'])
def mine_block():
    start_time = time.time()
    previous_block = blockchain.get_previous_block()

    # Mining Reward
    blockchain.add_transactions(node_address, 'Enaktar', 1)

    new_block = blockchain.create_block(previous_block['hash'])
    new_block['hash'] = blockchain.proof_of_work(new_block)
    blockchain.chain.append(new_block)
    response = {'message': 'Perfect! You just mined a block!',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'nonce': new_block['nonce'],
                'previous_hash': new_block['previous_hash'],
                'hash': new_block['hash'],
                'transactions': new_block['transactions'],
                'mining_elapsed_time': (time.time() - start_time)}
    return jsonify(response), 200


# Getting the full Blockchain

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The blockchain is not valid.'}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "Some elements of the transactions are missing!", 400
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201


# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': "All the nodes are now connected. The AGUcoin blockchain now contains the following nodes:",
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The blockchain is replaced by longest chain.',
                    'new_chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    return jsonify(response), 200

# Running the App
app.run(host='0.0.0.0', port=5002)
