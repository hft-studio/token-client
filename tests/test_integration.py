def test_mint_integration(token_client):
    test_wallet = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    
    # Test minting tokens
    receipt = token_client.mint(
        user_address=test_wallet,
        amount=1000
    )
    
    assert receipt['status'] == 1  # 1 means success in Ethereum receipts
    
    balance = token_client.contract.functions.balanceOf(test_wallet).call()
    assert balance >= 1000