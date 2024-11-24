import pytest
import subprocess
import time
from web3 import Web3
from pathlib import Path
import json
from token_client.client import TokenClient

@pytest.fixture(scope="session")
def anvil_process():
    # Start Anvil process
    process = subprocess.Popen(
        ["anvil"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Anvil to start
    time.sleep(2)
    
    yield process
    
    # Cleanup: terminate Anvil process
    process.terminate()
    process.wait()

@pytest.fixture(scope="session")
def web3(anvil_process):
    # Try to connect multiple times in case Anvil needs more time to start
    for _ in range(5):  # Try 5 times
        try:
            w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
            if w3.is_connected():
                return w3
        except:
            time.sleep(1)  # Wait 1 second between attempts
    
    # Final attempt
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    assert w3.is_connected()
    return w3

@pytest.fixture(scope="session")
def deployed_contract(web3):
    # Get the contract bytecode and abi
    contract_path = Path(__file__).parent.parent / "contracts" / "out" / "HFTToken.sol" / "HFTToken.json"
    with open(contract_path) as f:
        contract_json = json.loads(f.read())
    
    bytecode = contract_json['bytecode']['object']
    abi = contract_json['abi']
    
    # Deploy the contract
    Contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    acct = web3.eth.account.from_key('ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    
    construct_txn = Contract.constructor("HFT Token", "HFT").build_transaction({
        'from': acct.address,
        'nonce': web3.eth.get_transaction_count(acct.address),
        'gas': 1500000,
        'gasPrice': web3.eth.gas_price
    })
    
    signed = acct.sign_transaction(construct_txn)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt.contractAddress

@pytest.fixture
def test_rpc_url():
    return 'http://127.0.0.1:8545'  # Use local anvil URL instead of fake test URL

@pytest.fixture
def token_client(deployed_contract):
    return TokenClient(
        rpc_url="http://127.0.0.1:8545",
        private_key="ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        token_address=deployed_contract,
        contract_path="contracts/out/HFTToken.sol/HFTToken.json",
        chain_id=31337
    )