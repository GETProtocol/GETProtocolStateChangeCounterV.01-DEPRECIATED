#!/usr/bin/python
import os
# import pandas as pd
from io import StringIO
# import csv
# from typing import Optional, NamedTuple
from datetime import datetime
import pytz
import math

import config 
infura_config = config.infura_key
os.environ["WEB3_INFURA_PROJECT_ID"] = infura_config
from web3.auto.infura import w3

to_zone = 'Europe/Amsterdam'

def create_start_stop_schema(from_bheight, until_bheight, batch_size):

    bh_list = []
    diff_blocks = until_bheight - from_bheight

    amount_batches = math.ceil(diff_blocks / batch_size)

    step_start = from_bheight
    step_stop = from_bheight + batch_size

    for x in range(amount_batches):
        batch = [step_start, step_stop]
        bh_list.append(batch)

        step_start = step_stop + 1
        step_stop = step_stop + batch_size

        if until_bheight <= step_stop:
            batch = [step_start, until_bheight]
            bh_list.append(batch)
            return bh_list

def to_UTC_time(_timestamp):

    dt_objectstart = datetime.fromtimestamp(_timestamp)
    datetimeobject = dt_objectstart.replace(tzinfo=pytz.UTC)
    return datetimeobject.astimezone(pytz.timezone(to_zone)) #astimezone method

def ticket_matuation_to_dict(mutation: str, meta_data: dict):
    """
    Used in run_mutations to create a dict from. In order to

    Takes one mutation line of an IPFS batch
    Returns structured dictionary.
        -> INDEX of dataframe / database
        'statehash_tx': -> hash / receipt of state or mutation(n)
        'previous_statehash': -> hash / receipt of state or mutation(n-1)
        'input_message' : -> value inputted in message input (could be privId or eventId)
        'transition_type': -> type of mutation (w or f)
        'transition_id': -> id of the mutation
        'block_height': -> blockheight of the block anchoring the mutation.
        'block_timestamp': -> timestamp of the block anchorring the mutation.
        'transaction_hash': -> hash of the blockchain transaction that anchorred the tx.
        'IPFS_hash': -> hash of the IPFS file that contains the mutation
    """

    m = list(mutation.split(","))

    output_dict = {
        'statehash_tx': m[0],
        'previous_statehash': m[1],
        'transition_type': m[2],
        'transition_id': m[3],
        'input_message': str("null"),
        'block_height': meta_data["block_height"],
        'block_timestamp': meta_data["block_timestamp"],
        'transaction_hash': meta_data["transaction_hash"],
        'IPFS_hash': meta_data["IPFS_hash"]
    }

    return output_dict

def print_execution_time(start, end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return str("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
