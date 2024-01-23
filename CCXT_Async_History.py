from requests import get
from datetime import datetime
import ccxt.async_support as ccxt
import pandas as pd
import asyncio
from asyncio import get_event_loop
from aiolimiter import AsyncLimiter

from dotenv import load_dotenv
from pathlib import Path
import os

dotenv_path = Path('ccxt_config.env')
load_dotenv(dotenv_path=dotenv_path)

# Set rate limit for async function - allows for 1000 concurrent entries (MAX) within a 60-second window.
rate_limit = AsyncLimiter(1200,60)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 2000)

Api_Key = os.getenv('api')
BASE_URL = "https://api.etherscan.io/api"
ETH_VALUE = 10 ** 18


def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={Api_Key}"
    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url

async def fetch_ohlc(exchange, timestamp):
    async with rate_limit:
        price_response = await exchange.fetch_ohlcv('ETH/USDT', '1m', (timestamp * 1000), 1)
        return price_response[0][1]


async def main(address, startblock, endblock):
    # Default start block is 0, but you can change it depending on your needs
    get_transactions_url = make_api_url("account", "txlist", address, startblock=startblock, endblock=endblock, page=1,
                                        offset=10000, sort="asc")
    response = get(get_transactions_url)
    data = response.json()["result"]

    # Define binance as exchange for ccxt
    # Binance rate limit = 1200 requests per minute
    exchange = ccxt.binance()
    exchange.throttle.config['maxCapacity'] = 100000

    tasks = []
    empty_eth_df1 = pd.DataFrame()
    empty_eth_df2 = pd.DataFrame()

    for tx in data:
        to = tx["to"]
        from_addr = tx["from"]
        value = int(tx["value"]) / ETH_VALUE
        gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETH_VALUE
        hash = tx["hash"]
        time = datetime.fromtimestamp(int(tx["timeStamp"]))

        # Convert timestamp into int
        timestamp = int(tx['timeStamp'])

        # Make a new variable for an error code (1 or 0)
        error = int(tx['isError'])

        # Make an if/elif statement for the output and create a new variable (error2) that will either list the
        # transaction as a success or a failure.
        if error == 1:
            error2 = "Fail"
        else:
            error2 = "Success"

        empty_eth_df1 = empty_eth_df1.append(
            {
                'To': to,
                'From': from_addr,
                'Value': value,
                'Gas Used': gas,
                'Hash': hash,
                'Time': time,
                'Timestamp': timestamp,
                'Error Code': error,
                'TX Status': error2}, ignore_index=True)

    for tx in data:
        timestamp = int(tx['timeStamp'])
        tasks.append(asyncio.create_task(fetch_ohlc(exchange, timestamp)))

    price_list = await asyncio.gather(*tasks)

    for price in price_list:
        empty_eth_df2 = empty_eth_df2.append(
            {'ETH Price at TX': price}, ignore_index=True)

    await exchange.close()

    final_df = pd.concat([empty_eth_df1, empty_eth_df2], axis=1)
    print(final_df)
    final_df.to_csv('ETH Transactions 2.csv')


def get_block_by_timestamp(timestamp):
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={Api_Key}'
    response = get(url)
    data = response.json()
    block = data['result']
    return int(block)

def date_to_block(date):
    fmt = "%d/%m/%Y %H:%M:%S"
    block_time = int(time.mktime(time.strptime(f'{date} 00:00:00', fmt)))
    return get_block_by_timestamp(block_time)


if __name__ == '__main__':
    # 1. Enter address
    # 2. Enter start date (format: day/month/year ie. 1/10/2022)
    # 3. Enter end date (format: day/month/year ie. 1/10/22)
    # 4. START SCRIPT

    import time

    eth_address = input("Enter address: ")
    start_date = input("Enter start date (format: d/m/y - 01/10/2022): ")
    end_date = input("Enter end date (format: d/m/y - 01/10/2022): ")

    start = time.time()
    loop = get_event_loop()
    loop.run_until_complete(main(address=eth_address, startblock=date_to_block(start_date), endblock=date_to_block(end_date)))
    end = time.time()
    print(f'This took {end - start} seconds')
