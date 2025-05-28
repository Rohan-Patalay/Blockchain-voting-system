from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os
from blockchain import Blockchain
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize blockchain
blockchain = Blockchain(difficulty=2)

# Sample candidates
candidates = [
    {"id": "1", "name": "Candidate A"},
    {"id": "2", "name": "Candidate B"},
    {"id": "3", "name": "Candidate C"}
]

# Sample registered voters (in a real system, this would be in a secure database)
registered_voters = {
    "V1": {"password": "pass1", "name": "Voter 1", "voted": False},
    "V2": {"password": "pass2", "name": "Voter 2", "voted": False},
    "V3": {"password": "pass3", "name": "Voter 3", "voted": False},
    "V4": {"password": "pass4", "name": "Voter 4", "voted": False},
    "V5": {"password": "pass5", "name": "Voter 5", "voted": False},
    "admin": {"password": "admin123", "name": "Administrator", "voted": False}
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'voter_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'voter_id' not in session or session['voter_id'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        password = request.form['password']
        
        if voter_id in registered_voters and registered_voters[voter_id]['password'] == password:
            session['voter_id'] = voter_id
            session['name'] = registered_voters[voter_id]['name']
            
            if voter_id == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('vote'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('voter_id', None)
    session.pop('name', None)
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if session['voter_id'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # Check if voter has already voted
    voter_id = session['voter_id']
    for block in blockchain.chain:
        for vote in block.votes:
            if vote['voter_id'] == voter_id:
                return render_template('already_voted.html')
    
    for vote in blockchain.pending_votes:
        if vote['voter_id'] == voter_id:
            return render_template('already_voted.html')
    
    if request.method == 'POST':
        candidate_id = request.form['candidate']
        if blockchain.add_vote(voter_id, candidate_id):
            registered_voters[voter_id]['voted'] = True
            return render_template('vote_success.html')
        else:
            return render_template('already_voted.html')
    
    return render_template('vote.html', candidates=candidates)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/mine', methods=['POST'])
@admin_required
def mine():
    if not blockchain.pending_votes:
        return jsonify({"message": "No pending votes to mine"}), 400
    
    block = blockchain.mine_pending_votes()
    return jsonify({
        "message": "Block mined successfully",
        "block": {
            "index": block.index,
            "timestamp": block.timestamp,
            "votes": len(block.votes),
            "hash": block.hash
        }
    })

@app.route('/admin/results')
@admin_required
def results():
    results = blockchain.get_results()
    formatted_results = []
    
    for candidate in candidates:
        candidate_id = candidate['id']
        votes = results.get(candidate_id, 0)
        formatted_results.append({
            "id": candidate_id,
            "name": candidate['name'],
            "votes": votes
        })
    
    return render_template('results.html', results=formatted_results)

@app.route('/admin/blockchain')
@admin_required
def view_blockchain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "votes": len(block.votes),
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce
        })
    
    return render_template('blockchain.html', chain=chain_data, pending_votes=len(blockchain.pending_votes))

@app.route('/blockchain/visual')
@admin_required
def blockchain_visual():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "votes": len(block.votes),
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce
        })
    
    return render_template('blockchain_visual.html', chain=chain_data)

@app.route('/api/block/<int:block_index>/votes')
@admin_required
def get_block_votes(block_index):
    if block_index < 0 or block_index >= len(blockchain.chain):
        return jsonify({"error": "Block not found"}), 404
    
    block = blockchain.chain[block_index]
    
    # Add candidate names to votes
    votes_with_names = []
    for vote in block.votes:
        vote_data = vote.copy()  # Create a copy to avoid modifying the original
        votes_with_names.append(vote_data)
    
    return jsonify({"votes": votes_with_names})

@app.route('/api/validate')
@admin_required
def validate_blockchain():
    is_valid = blockchain.is_chain_valid()
    
    if is_valid:
        return jsonify({"valid": True})
    else:
        
        return jsonify({
            "valid": False,
            "invalid_block": len(blockchain.chain) - 1  # Assume the last block is invalid
        })

if __name__ == '__main__':
    app.run(debug=True)