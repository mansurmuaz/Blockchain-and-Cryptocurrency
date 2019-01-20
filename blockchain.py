#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modele 1 - Create BlockChain

import datetime
import hashlib
import json
from flask import Flask, jsonify
from random import randint

import time


# Part 1 - Building BlockChain

class Blockchain:

    difficulty = 5
    leading_zeros = '00000'

    def __init__(self):
        self.chain = []
        self.chain.append(self.create_block(previous_hash='0'))
        self.chain[0]['hash'] = self.proof_of_work(self.chain[0])

    def create_block(self, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': '',
                 'data': randint(100, 99999999),
                 'nonce': 0,
                 'previous_hash': previous_hash,
                 'hash': ""}
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


# Part 2 - Mining BlockChain
# Create a Web App
app = Flask(__name__)

# Create a Blockhain Instance

blockchain = Blockchain()


# Mining a new block

@app.route('/mine_block', methods=['GET'])
def mine_block():
    start_time = time.time()
    previous_block = blockchain.get_previous_block()
    new_block = blockchain.create_block(previous_block['hash'])
    new_block['hash'] = blockchain.proof_of_work(new_block)
    blockchain.chain.append(new_block)
    response = {'message': 'Perfect! You just mined a block!',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'data':new_block['data'],
                'nonce': new_block['nonce'],
                'previous_hash': new_block['previous_hash'],
                'hash': new_block['hash'],
                'minig_elapsed_time': (time.time() - start_time)}
    return jsonify(response), 200


# Getting the full Blockchain

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain}
    return jsonify(response), 200


@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The blockchain is not valid.'}
    return jsonify(response), 200


# Running the App
app.run(host='127.0.0.1', port=5000)
