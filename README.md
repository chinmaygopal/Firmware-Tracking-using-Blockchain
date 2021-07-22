Since we use Hyperledger Fabric please install the prerequisites as mentioned in the [link](https://hyperledger-fabric.readthedocs.io/en/latest/prereqs.html)
For the initial setup, the tutorial in [link](https://www.youtube.com/watch?v=SJTdJt6N6Ow&list=PLSBNVhWU6KjW4qo1RlmR7cvvV8XIILub6) was used.  
For our project to run the Blockchain:
1. Navigate to the _artifacts_ folder and execute ``docker-compose up -d --remove-orphan``
2. Return to the main folder i.e. _Firmware-Tracking-using-Blockchain_ and execute the following commands:  
   ``./createChannel.sh``   
   ``./deployChaincode.sh``  
This should get the Blockchain environment running.
3. Next in the _api-firmwareupdate_ folder execute the ``node app``