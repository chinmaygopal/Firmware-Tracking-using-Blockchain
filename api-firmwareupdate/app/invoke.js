const { Gateway, Wallets, TxEventHandler, GatewayOptions, DefaultEventHandlerStrategies, TxEventHandlerFactory } = require('fabric-network');
const fs = require('fs');
const path = require("path")
const log4js = require('log4js');
const logger = log4js.getLogger('BasicNetwork');
const util = require('util')

const helper = require('./helper')

const invokeTransaction = async (channelName, chaincodeName, fcn, args, username, org_name, transientData) => {
    try {
        logger.debug(util.format('\n============ invoke transaction on channel %s ============\n', channelName));

        // load the network configuration
        // const ccpPath =path.resolve(__dirname, '..', 'config', 'connection-org1.json');
        // const ccpJSON = fs.readFileSync(ccpPath, 'utf8')
        const ccp = await helper.getCCP(org_name) //JSON.parse(ccpJSON);

        // Create a new file system based wallet for managing identities.
        const walletPath = await helper.getWalletPath(org_name) //path.join(process.cwd(), 'wallet');
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        // Check to see if we've already enrolled the user.
        let identity = await wallet.get(username);
        if (!identity) {
            console.log(`An identity for the user ${username} does not exist in the wallet, so registering user`);
            await helper.getRegisteredUser(username, org_name, true)
            identity = await wallet.get(username);
            console.log('Run the registerUser.js application before retrying');
            return;
        }

        

        const connectOptions = {
            wallet, identity: username, discovery: { enabled: true, asLocalhost: true },
            eventHandlerOptions: {
                commitTimeout: 100,
                strategy: DefaultEventHandlerStrategies.NETWORK_SCOPE_ALLFORTX
            }
            // transaction: {
            //     strategy: createTransactionEventhandler()
            // }
        }

        // Create a new gateway for connecting to our peer node.
        const gateway = new Gateway();
        await gateway.connect(ccp, connectOptions);

        // Get the network (channel) our contract is deployed to.
        const network = await gateway.getNetwork(channelName);

        const contract = network.getContract(chaincodeName);

        let result
        let message;
        if (fcn === "addFirmwareUpdate") {
            result = await contract.submitTransaction(fcn, args[0], args[1], args[2], args[3], args[4]);
            message = `Successfully added the firmware with key firmware_${args[1]}`

        } else if (fcn === "addDeviceForUpdate") {
            result = await contract.submitTransaction(fcn, args[0], args[1], args[2]);
            message = `Successfully added device for update with key update_${args[1]}_${args[0]}`
    
        } else if (fcn === "changeUpdateProgress") {
            result = await contract.submitTransaction(fcn, args[0], args[1],args[2]);
            message = `Successfully changed update progress ${args[0]}`

        } else if (fcn === "getUpdateProgress") {
            result = await contract.submitTransaction(fcn, args[0], args[1]);
            message = `Got update progress`
            
        } else if (fcn === "queryFirmware") {
            result = await contract.submitTransaction(fcn, args[0]);
            message = `Successfully changed car owner with key ${result}`

        } else if (fcn === "compareFileHash") {
            console.log("print compareFileHash");
            result = await contract.submitTransaction(fcn, args[0]);
            console.log("print got result");
            message = `Successfully compared file hash ${result}`

        } else if (fcn === "addLatestFirmwareHash") {
            console.log("print compareFileHash");
            result = await contract.submitTransaction(fcn, args[0]);
            console.log("print got result");
            message = `Successfully added file hash ${ args[0]}`

        } else if (fcn === "getLatestFirmwareHash") {
            console.log("print compareFileHash");
            result = await contract.submitTransaction(fcn);
            console.log("print got result");
            message = `Got the latest file hash`

        }
        else {
            return `Invocation require either createCar or changeCarOwner as function but got ${fcn}`
        }

        await gateway.disconnect();

        result = JSON.parse(result.toString());

        let response = {
            message: message,
            result
        }

        return response;


    } catch (error) {

        console.log(`Getting error: ${error}`)
        return error.message

    }
}

exports.invokeTransaction = invokeTransaction;