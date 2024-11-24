from web3 import Web3
from hexbytes import HexBytes
from eth_typing import HexStr
from web3.types import Wei

def convert_web3_types(obj):
    """
    Convert Web3 specific types to JSON serializable formats
    """
    if isinstance(obj, dict):
        return {key: convert_web3_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_web3_types(item) for item in obj]
    elif hasattr(obj, 'hex'):  # Check if object has hex method instead of checking type
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    return obj