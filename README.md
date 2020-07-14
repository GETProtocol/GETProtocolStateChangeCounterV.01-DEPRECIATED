# GET Protocol state change counter 
Integrators of the GET Protocol(ticketing companies) are required to use GET as fuel in order to use the features. This tool allows the community to track and verify the usage of GET in the past. 

This script found in this repo queries the GET Protocol anchoring contract between provided blockheights. All the IPFS batches found will be extracted/downloaded and stored to a pandas dataframe. After the last batch in the blockheight range has been extracted the dataframes will be stored in .csv format. 

### !! Be aware that script can have a long run-time !!
Depending on the start and stop height that is defined, it might take a while before the script terminates. This is because all IPFS batches are pulled from the ETH anchor contract one by one. 

Take note that this long duration isn't due to Ethereum to be slow or because the script is overly complex. The process that requires the most time is downloading/pulling of the mutation files from IPFS. Similar to how it can take a while before a blockchain is fully synced up.


###### Example values: 2020 Q2 blockheights:
_startheight=9743576 \
_stopheight=10338066

Use the ethereum blockchain explorer like blockchair to figure out what blockheight constitutes to a certain moment in time: https://blockchair.com/ethereum/blocks?s=time(desc)&q=time(2020-03-31)#

The result of this range will result in a total state change count of xx tx's.

#### Requirements / Installation
- Set up venv in root folder
- Install required packages (pipenv)
- Set up an account with etherscan.com ond obtain 
- Set up a free account wit

##### Set enviroment variables 
- Configure Infura API keys (free) -> config.py
- Etherscan API keys (free account) -> config.py

#### Usage (VirtualEnv)

Make sure you have installed venv (pip install virtualenv). Then while in the root folder of this repo:
``` 
$ virtualenv venv
```
Done? Great. Next up, activate the venv.
``` 
$ source venv/bin/activate
```
To properly manage all required package we use pipenv. 
``` 
$ pip install pipenv
```
Done.

After having set up the requirments it is possible to run a count of the state changes registered between the provided blockheight: 
``` 
$ python import_IPFS.py --startheight <INTEGER> --stopheight <INTEGER> 
```
Depending on the provided blockheights, this can take between a few minutes to an hour (or more).

#### Usage (Docker)

```
docker build -t counter .
docker run counter --startheight <INTEGER> --stopheight <INTEGER>
```

We then extract the csv results from the container. For that, first we find the container ID and then we copy as:
```
docker ps -alq
docker cp <PREVIOUS_COMMAND_RESULT>:/code/count_results .
```

You'll find the results under the folder `./count_results` on your local directory
