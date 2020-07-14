#!/usr/bin/python
import os
from io import StringIO
import csv
import pandas as pd
import time
import math
import requests
import sys
from run_mutations import extract_all_statachanges_from_df, IPFS_tx_count
from utilities import print_execution_time, str2bool, to_UTC_time, create_start_stop_schema
from solidity.abi import abi
import argparse

import config
eth_base_url = config.eth_base_url
eth_api_token = config.eth_api_token
api_base_url = config.api_base_url
anchor_contract = config.anchor_contract
infura_config = config.infura_key

os.environ["WEB3_INFURA_PROJECT_ID"] = infura_config
from web3.auto.infura import w3

def decode_input_to_string(tx_hash: str) -> str:
    """ Reads and decodes the input of a transaction of a Ethereum contract call.
    tx_hash -> ETH transaction hash.
    Returns IPFSpointer (string) of  the IPFS batch registered by contract (str) on a certain blockheight
    """

    hash_input = "null"
    contract = w3.eth.contract(address = anchor_contract, abi = abi)

    try: # request transaciton information from etherscan
        transaction = w3.eth.getTransaction(tx_hash)
    except Exception as e: # decoding of tx input failed
        print("Transaction hash: %s cannot be decoded error %s. hash_input='null'." % (tx_hash, e))
    else: # use contract abi to decode the input message
        decoded_input = list(contract.decode_function_input(transaction.input))
        hash_input = decoded_input[1]['_ipfsHash']
    finally:
        return hash_input


def etherscan_api_call(start_height, stop_height):
    api_url = f"{eth_base_url}{anchor_contract}&startblock={start_height}&endblock={stop_height}&sort=asc&apikey={eth_api_token}"
    return requests.get(api_url)

def fetch_blocks_in_range(start_height, stop_height, batch_size):
    """ Lookup all the IPFS hashes in the Etherscan smart contract.
    Pulls all transactions-ids to explore from Etherscan.
    As ES uses batch maximums this function splits the 'to explore' transactions in batches (batch_size)
        start_height: starting block height
        stop_height: stopping blokc
        batch_size: batch size for Etherscan request 
    """

    df_ethscan = pd.DataFrame() # emtpy dataframe to store found batches

    if stop_height == None: # if no ending height is provided
        last_blockheight = w3.eth.blockNumber # count statechanges until most recent block
    else:
        last_blockheight = stop_height

    start_timestamp = w3.eth.getBlock(start_height).timestamp
    time_amsterdamstart = to_UTC_time(start_timestamp)

    end_timestamp = w3.eth.getBlock(last_blockheight).timestamp
    time_amsterdamsstop = to_UTC_time(end_timestamp)

    print(f"\nStart of count at blockheight {start_height} timestamped on {time_amsterdamstart}.\n")
    print(f"Stop of count at blockheight {last_blockheight} timestamped on {time_amsterdamsstop}.\n")

    diff_blocks = last_blockheight - start_height

    print(f"Amount of Ethereum blocks to explore for registered statechanges: {diff_blocks} \n")

    # Etherscan has limits to how large queries can be. So we cut the full range up in smaller intervals.
    import_schema = create_start_stop_schema(from_bheight=start_height, until_bheight=last_blockheight, batch_size=batch_size)

    for b in import_schema: # iterate over the interval schema
        try:
            batch = etherscan_api_call(b[0],b[1])
        except Exception as e: # something went wrong getting the transactions from etherscan
            print(f"Error in get_all_blocks. Batch: {b+1}. Error: {e}. EXIT QUERY")
            sys.exit() # A missing etherscan batch will corrupt the entire count. So; exit and retry.
        else:
            api_return_json = batch.json()
            df_ethscan = df_ethscan.append(api_return_json['result'], ignore_index=True)

    df_ethscan.insert(loc=4,column="IPFS_hash", value='null') # insert column for the IPFS batches
    df_ethscan.insert(loc=5,column="statechange_count", value='null') # insert column for the statechange counts

    df_return = df_ethscan.rename(columns={"blockNumber": "block_height", "timeStamp":"block_timestamp", "hash": "transaction_hash"})
    
    return df_return

def lookup_IPFS_hash_to_dataframe(df_e: object):
    """ Decodes the contact input that was registered by Stoolbox in a solidity contract.
    Returns dataframe with the decoded hash filled in. 
    """

    df_filled = df_e.copy()

    for i, row in df_filled.iterrows():
        hash_row = row["transaction_hash"]
        try: # read and decode the input tx with the solidity contract ABI
            input_value = decode_input_to_string(hash_row)
            _count = IPFS_tx_count(input_value)

            df_filled.at[i, 'IPFS_hash'] = input_value # store hash in dataframe
            df_filled.at[i, 'statechange_count'] = _count # store hash in dataframe

        except Exception as e:
            # print(f"Something went wrong in decoding! hashrow: {hash_row} error: {e}")
            df_filled.drop(df_filled.index[i])
            print(f"IPFS dataframe row {i} dropped! because hash: {hash_row} couldn't be interpreted. error: {e}")

    return df_filled


def conduct_count_statechanges(start_height=10326205, stop_height=None, only_count=False):
    start = time.time()
    batch_size=8500 # TODO make batch_size dynamic

    csv=True

    # Step 1. Create dataframe with all IPFS batches in range
    df_batches = fetch_blocks_in_range(start_height=start_height, stop_height=stop_height, batch_size=batch_size)
    df_IPFS = lookup_IPFS_hash_to_dataframe(df_batches)


    ipfs_count = df_IPFS.shape[0]
    print(f"\n Amount of IPFS batches registered in range: {ipfs_count} \n")
    results_dir = "count_results"

    filename_IPFS = f"exportIPFS_blockheight_{start_height}_stopheight_{stop_height}.csv"
    filename_statechanges = f"exportstatechanges_blockheight_{start_height}_stopheight_{stop_height}.csv"
    results_dir = "count_results"

    if only_count == True: # only count the state changes in a batch, do not store them locally
        df_IPFS_final = df_IPFS[['block_height', 'block_timestamp','IPFS_hash', 'statechange_count']]
        
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
        df_IPFS_final.to_csv(f'count_results/{filename_IPFS}')

        count_data = {
            "df_IPFS": df_IPFS_final,
            "df_stc": None,
        }
        end = time.time()
        needed_time = print_execution_time(start, end)
        print(f"Time needed to extract IPFS table: {needed_time}")
        return count_data

    else:
        # Step 2. Create dataframe with all statechanges found in the IPFS dataframe
        df_stc = extract_all_statachanges_from_df(df_IPFS)
        batch_count = df_stc.shape[0]
        print(f"\nBetween blockheight:{start_height} and {stop_height} a total of {batch_count} statechanges been registered.\n")

        # Select only columns that make any sense to store.
        df_IPFS_final = df_IPFS[['block_height', 'block_timestamp','IPFS_hash', 'statechange_count']]
        df_stc_final = df_stc[['statehash_tx', 'previous_statehash', 'transition_type', 'transition_id', 'block_height', 'IPFS_hash']]

        if csv == True: # Optional. Store csv files to local storage
            if not os.path.exists(results_dir):
                os.mkdir(results_dir)
            df_IPFS_final.to_csv(f'count_results/{filename_IPFS}')
            df_stc_final.to_csv(f'count_results/{filename_statechanges}')

        count_data = {
            "df_IPFS": df_IPFS_final,
            "df_stc": df_stc_final,
        }
        end = time.time()
        needed_time = print_execution_time(start, end)
        print(f"Time needed to build/extract IPFS & mutation: {needed_time}\n\n")
        return count_data


def explorer_query_parser():
    sb_parser = argparse.ArgumentParser(description='Blockheight range to query the anchoring contract between.')

    sb_parser.add_argument('--startheight',
                        type=int,
                        default=9743576,
                        help='Starting block of the count. This block will be the first block in the range to be included in export + count.')

    sb_parser.add_argument('--stopheight',
                        type=int,
                        default=10338066,
                        help='Stop block of the count. This block will be the last block in the range to be included in export + count.')
    arguments = sb_parser.parse_args()
    return arguments


if __name__ == '__main__':
    # Example queries to play around 
    # Short execution time(10k blocks -> 36-100 seconds): 
    # venv: python import_IPFS.py --startheight=10328066 --stopheight=10338066
    # docker run counter --startheight 10328066 --stopheight 10338066
    # Medium execution time(300k blocks -> 18 minutes) 
    # venv: python import_IPFS.py --startheight=10038066 --stopheight=10338066 
    # docker run counter --startheight 10038066 --stopheight 10338066
    # Long execution time(600k blocks -> 20-40 minutes): 
    # venv: python import_IPFS.py --startheight=9743576 --stopheight=10338066  THIS IS THE Q2 2020 RANGE
    # docker run counter --startheight 9743576 --stopheight 10338066
    
    args = explorer_query_parser()
    startheight = args.startheight
    stopheight = args.stopheight

    _count = False

    assert startheight < stopheight, "startheight cannot be larger as the stopheight. Please check the range."

    dict_results = conduct_count_statechanges(start_height=startheight, stop_height=stopheight, only_count=_count)