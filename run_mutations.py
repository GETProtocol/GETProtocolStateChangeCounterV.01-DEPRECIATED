#!/usr/bin/python
import pandas as pd
import os
import sys
import ipfsapi

api = ipfsapi.connect('https://ipfs.infura.io', 5001)
from utilities import print_execution_time, ticket_matuation_to_dict, str2bool


def IPFS_file_pull(lookup_hash: str):
    """ Fetches data and returns dump of IPFS file """
    file_ipfs = api.cat(lookup_hash) # fetch the file from IPFS
    mutation_dump = file_ipfs.decode('utf-8').splitlines() # split the dump into a nested list
    return mutation_dump


def IPFS_tx_count(lookup_hash: str):
    file_ipfs = api.cat(lookup_hash) # fetch the file from IPFS
    return len(file_ipfs.decode('utf-8').splitlines()) # split the dump into a nested list

def extract_all_statachanges_from_df(IPFS_dataframe):
    """ Stores all the mutations found in a list of IPFS hashes to a dataframe. """

    appended_data = []

    for i, row in IPFS_dataframe.iterrows():  # Iterate over the IPFS batches
        hash_pointer = row["IPFS_hash"]

        block_data = {
            "block_height": row["block_height"],
            "block_timestamp": row["block_timestamp"],
            "transaction_hash": row["transaction_hash"],
            "IPFS_hash": hash_pointer
        }

        if hash_pointer == 'null': # skip empty transactions
            print(f"Hash pointer is null. Row: {row['transaction_hash']}. Height: {row['block_timestamp']}")
        elif len(hash_pointer) != 46:
            print(f"Length of hash isn't 47. Row: {row['transaction_hash']}. Height: {row['block_timestamp']}")

        else:
            try: # lookup/download of the pinned IPFS batch
                mutation_dump = IPFS_file_pull(hash_pointer)
            except Exception as e:
                print("Error in extract_all_mutations_to_df_from_df: %s" % e)
            batch_list = []
            for x in range(len(mutation_dump)):
                _row = ticket_matuation_to_dict(mutation_dump[x], block_data)
                batch_list.append(_row)
            batch_df = pd.DataFrame(batch_list)
            appended_data.append(batch_df)

    concat_df = pd.concat(appended_data)
    return concat_df
