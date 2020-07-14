abi = [
    {
        "constant": True,
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "batches",
        "outputs": [{"internalType": "string", "name": "ipfsHash", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"internalType": "string", "name": "_ipfsHash", "type": "string"}],
        "name": "registerBatch",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "ipfsHash",
                "type": "string",
            }
        ],
        "name": "Update",
        "type": "event",
    },
]