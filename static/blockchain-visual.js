document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('blockDetailsModal');
    const modalContent = document.getElementById('blockDetailsContent');
    const closeModal = document.querySelector('.close-modal');
    
    // Close modal when clicking the X
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // View votes buttons
    const viewVotesButtons = document.querySelectorAll('.view-votes-btn');
    viewVotesButtons.forEach(button => {
        button.addEventListener('click', function() {
            const blockIndex = this.getAttribute('data-index');
            fetchBlockVotes(blockIndex);
        });
    });
    
    // Validate blockchain button
    const validateButton = document.getElementById('validateChain');
    const validationResult = document.getElementById('validationResult');
    
    validateButton.addEventListener('click', function() {
        validateBlockchain();
    });
    
    // Function to fetch block votes
    function fetchBlockVotes(blockIndex) {
        fetch(`/api/block/${blockIndex}/votes`)
            .then(response => response.json())
            .then(data => {
                displayBlockVotes(data, blockIndex);
            })
            .catch(error => {
                console.error('Error fetching block votes:', error);
                modalContent.innerHTML = `<div class="alert error">Error loading block data</div>`;
                modal.style.display = 'block';
            });
    }
    
    // Function to display block votes in modal
    function displayBlockVotes(data, blockIndex) {
        let content = `<h4>Block #${blockIndex} Votes</h4>`;
        
        if (data.votes && data.votes.length > 0) {
            content += `
                <table class="votes-table">
                    <thead>
                        <tr>
                            <th>Voter ID</th>
                            <th>Candidate</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.votes.forEach(vote => {
                const date = new Date(vote.timestamp * 1000).toLocaleString();
                const candidateName = getCandidateName(vote.candidate_id);
                
                content += `
                    <tr>
                        <td>${vote.voter_id}</td>
                        <td>${candidateName}</td>
                        <td>${date}</td>
                    </tr>
                `;
            });
            
            content += `
                    </tbody>
                </table>
            `;
        } else {
            content += `<div class="alert info">No votes in this block</div>`;
        }
        
        modalContent.innerHTML = content;
        modal.style.display = 'block';
    }
    
    // Function to get candidate name from ID
    function getCandidateName(candidateId) {
        const candidates = {
            "1": "Candidate A",
            "2": "Candidate B",
            "3": "Candidate C"
        };
        
        return candidates[candidateId] || `Unknown (${candidateId})`;
    }
    
    // Function to validate blockchain
    function validateBlockchain() {
        fetch('/api/validate')
            .then(response => response.json())
            .then(data => {
                displayValidationResult(data);
            })
            .catch(error => {
                console.error('Error validating blockchain:', error);
                validationResult.className = 'alert error';
                validationResult.innerHTML = 'Error validating blockchain';
                validationResult.style.display = 'block';
            });
    }
    
    // Function to display validation result
    function displayValidationResult(data) {
        const blocks = document.querySelectorAll('.block-visual');
        
        if (data.valid) {
            validationResult.className = 'alert success';
            validationResult.innerHTML = 'Blockchain is valid! All blocks are correctly linked.';
            
            blocks.forEach(block => {
                block.classList.remove('invalid-block');
                block.classList.add('valid-block', 'validation-animation');
                setTimeout(() => {
                    block.classList.remove('validation-animation');
                }, 1000);
            });
        } else {
            validationResult.className = 'alert error';
            validationResult.innerHTML = `Blockchain validation failed at block #${data.invalid_block}`;
            
            blocks.forEach(block => {
                const blockIndex = parseInt(block.getAttribute('data-index'));
                
                if (blockIndex >= data.invalid_block) {
                    block.classList.remove('valid-block');
                    block.classList.add('invalid-block', 'validation-animation');
                } else {
                    block.classList.remove('invalid-block');
                    block.classList.add('valid-block');
                }
                
                setTimeout(() => {
                    block.classList.remove('validation-animation');
                }, 1000);
            });
        }
        
        validationResult.style.display = 'block';
    }
});