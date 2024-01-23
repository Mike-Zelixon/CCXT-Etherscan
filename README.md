# CCXT-Etherscan
Used for tracking the transaction history of any ETH account with relevant prices at the time of transaction, for any given date range. 

Returns a complete CSV of transaction history, most notably with the ETH price at the time of the transaction for accounting purposes. 

The regular Etherscan API does NOT provide this feature (price @ time of TX) therefore CCXT was used.

The script uses asyncio to speed up potential 10's of thousands of transactions to go and process.

![alt text](https://etherscan.io/images/brandassets/etherscan-logo.svg)

