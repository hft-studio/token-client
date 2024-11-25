# Token Client

A Python client for interacting with HFT tokens on the blockchain.

## Installation

Clone this repository with submodules:

```bash
git clone --recurse-submodules <repository-url>
cd token-client
pip install -e ".[dev]"
```

If you already cloned without submodules, run these commands from the project root:
```bash
git submodule init
git submodule update
pip install -e ".[dev]"
```

## Running Tests

Before running tests, you'll need to:

1. Build the smart contracts:
```bash
cd contracts
forge build
cd ..
```

2. Then run the tests:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_specific.py
```

If you get contract-related errors, ensure:
- Submodules are properly initialized (`git submodule init && git submodule update`)
- Contracts are built successfully (`forge build` outputs no errors)
- You're running commands from the project root directory
