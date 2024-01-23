# CCXT-Etherscan
Used for tracking TX history of any ETH account with relevant prices at the time of TX 

Useful script that utilizes asyncronous functions using the CCXT library along with the Etherscan API.

Takes any ETH address you put into the prompt along with a selected date range.

Returns a complete CSV of transaction history, most notably with the ETH price at the time of the transaction for accounting purposes. 

The regular Etherscan API does NOT provide this feature (price @ time of TX) therefore CCXT was used.
