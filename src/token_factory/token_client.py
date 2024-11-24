from pathlib import Path
from web3 import Web3
import json
from typing import Union
from .utils.web3_utils import convert_web3_types

class TokenClient:
    def __init__(
        self, 
        rpc_url: str, 
        private_key: str, 
        token_address: str, 
        contract_path: Union[str, Path],
        chain_id: int = 31337
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        self.chain_id = chain_id
        
        # Load contract ABI
        contract_path = Path(contract_path)
        with open(contract_path) as f:
            contract_json = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=token_address,
            abi=contract_json['abi']
        )
    
    def mint(self, user_address: str, amount: int, max_retries: int = 3) -> dict:
        try:
            # Validate inputs
            if not isinstance(user_address, str):
                raise TypeError("user_address must be a string")
            if not isinstance(amount, (int, float)):  # Make sure we use proper types here
                raise TypeError("amount must be a number")
            
            contract_address = self.contract.address
            print(f"Using contract address: {contract_address}")
            
            # Verify the contract exists at this address
            code = self.w3.eth.get_code(contract_address)
            print(f"Contract bytecode length: {len(code)}")
            if code == b'' or code == '0x':
                raise ValueError("No contract found at the specified address")
            
            # Get the sender's address
            sender_address = self.w3.eth.account.from_key(self.private_key).address
            print(f"Sending from address: {sender_address}")
            
            # Debug contract state
            try:
                # Try to get contract name and symbol first
                name = self.contract.functions.name().call()
                symbol = self.contract.functions.symbol().call()
                print(f"Contract name: {name}")
                print(f"Contract symbol: {symbol}")
            except Exception as e:
                print(f"Error getting token info: {str(e)}")
            
            try:
                contract_owner = self.contract.functions.owner().call()
                print(f"Contract owner: {contract_owner}")
                is_paused = self.contract.functions.paused().call()
            except Exception as e:
                print(f"Error checking contract state: {str(e)}")
                raise ValueError("Failed to interact with contract")
            
            print(f"Contract state:")
            print(f"- Is paused: {is_paused}")
            print(f"- Contract owner: {contract_owner}")
            print(f"- Sender is owner: {contract_owner.lower() == sender_address.lower() if contract_owner else 'Unknown'}")
            
            # Check if contract is paused
            if is_paused:
                raise ValueError("Contract is paused")
            
            # Check if sender is owner
            if contract_owner and contract_owner.lower() != sender_address.lower():
                raise ValueError("Sender is not the contract owner")
            
            # Try to simulate the transaction
            try:
                self.contract.functions.mint(
                    user_address,
                    amount
                ).call({'from': sender_address})
            except Exception as call_error:
                error_details = str(call_error)
                if hasattr(call_error, 'args') and len(call_error.args) > 0:
                    error_details = call_error.args[0]
                raise ValueError(f"Transaction would fail: {error_details}")

            nonce = self.w3.eth.get_transaction_count(self.w3.eth.account.from_key(self.private_key).address)

            # Build mint transaction
            mint_txn = self.contract.functions.mint(
                user_address,
                amount
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 200000,
                'maxFeePerGas': self.w3.eth.gas_price,
                'nonce': nonce,
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(mint_txn, self.private_key)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Check transaction status
            if tx_receipt['status'] == 0:
                raise ValueError("Transaction failed")
            
            # Convert Web3 types to JSON serializable types
            return convert_web3_types(dict(tx_receipt))
            
        except Exception as e:
            print(f"Error minting tokens: {str(e)}")
            raise
    