import hashlib
import json
import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, timestamp: float, votes: List[Dict[str, Any]], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.votes = votes
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": self.votes,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"Block mined: {self.hash}")

class Blockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_votes: List[Dict[str, Any]] = []
        self.difficulty = difficulty
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        genesis_block = Block(0, time.time(), [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print("Genesis block created")
    
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    
    def add_vote(self, voter_id: str, candidate_id: str) -> bool:
        # Check if voter has already voted
        for block in self.chain:
            for vote in block.votes:
                if vote["voter_id"] == voter_id:
                    return False
        
        for vote in self.pending_votes:
            if vote["voter_id"] == voter_id:
                return False
        
        self.pending_votes.append({
            "voter_id": voter_id,
            "candidate_id": candidate_id,
            "timestamp": time.time()
        })
        return True
    
    def mine_pending_votes(self) -> Block:
        if not self.pending_votes:
            return None
        
        latest_block = self.get_latest_block()
        new_block = Block(
            latest_block.index + 1,
            time.time(),
            self.pending_votes,
            latest_block.hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_votes = []
        return new_block
    
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if hash is correctly calculated
            if current_block.hash != current_block.calculate_hash():
                print("Invalid hash")
                return False
            
            # Check if current block points to the correct previous hash
            if current_block.previous_hash != previous_block.hash:
                print("Invalid previous hash reference")
                return False
        
        return True
    
    def get_results(self) -> Dict[str, int]:
        results = {}
        
        for block in self.chain:
            for vote in block.votes:
                candidate_id = vote["candidate_id"]
                if candidate_id in results:
                    results[candidate_id] += 1
                else:
                    results[candidate_id] = 1
        
        return results