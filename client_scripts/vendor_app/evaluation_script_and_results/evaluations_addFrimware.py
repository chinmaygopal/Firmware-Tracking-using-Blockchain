import http.client
import json
import time

token = ""

def register_user():
    conn_blk_chain = http.client.HTTPConnection("localhost:4000")
    headers = {'Content-type': 'application/json'}
    foo = {
        "username": "chinmay3",
        "orgName": "Org1"
    }
    json_data = json.dumps(foo)
    conn_blk_chain.request('POST', '/users', json_data, headers)
    response = conn_blk_chain.getresponse()
    global token
    token = json.loads(response.read().decode())["token"]
    conn_blk_chain.close()

class BlockchainInteractions:
    def __init__(self):
        self.__fcn = ""
        self.__args = ""
        self.__dev_id = "RPi2"
        self.__hash_str = "e3477a6037d9e61fb4768ebc0bc222614cb4bb57cf37f9b3b569375a90b7b314"
        self.__version = 1

    def set_fcn(self, fcn):
        self.__fcn = fcn

    def set_args(self, args):
        self.__args = args

    def set_hash(self, hash_str):
        self.__hash_str = hash_str

    def block_chain_interaction(self):
        global token
        conn_blk_chain = http.client.HTTPConnection("localhost:4000")

        headers = {'Content-type': 'application/json', 'Authorization':
            'Bearer ' + str(token)}

        foo = {
            "fcn": self.__fcn,
            "peers": ["peer0.org1.firmwareupdate.com", "peer0.org2.firmwareupdate.com"],
            "chaincodeName": "firmware_update_contract",
            "channelName": "mychannel",
            "args": self.__args
        }
        json_data = json.dumps(foo)

        try:
            conn_blk_chain.request('POST', '/channels/mychannel/chaincodes/firmware_update_contract', json_data, headers)

            response = conn_blk_chain.getresponse()
        except http.client.RemoteDisconnected:
            exit(1)

        resp_str = json.loads(response.read().decode())
        conn_blk_chain.close()
        return resp_str

    def check_for_latest_update(self):
        self.__fcn = "compareFileHash"
        self.__args = [self.__hash_str]
        return_val = [self.__hash_str, False]
        resp = self.block_chain_interaction()

        resp_hash = resp["result"]["result"]["file_hash"]

        if self.__hash_str != resp_hash:
            self.__hash_str = resp_hash
            print("changed hash")
            return_val = [resp_hash, True]
        return return_val

    def add_device_for_update(self):
        self.__fcn = "addDeviceForUpdate"
        self.__args = [self.__hash_str, self.__dev_id, "Started"]
        self.block_chain_interaction()

    def add_firmware_update(self, hash_val, filesize):
        self.__fcn = "addFirmwareUpdate"
        self.__args = ["temp_reader_v2.py", str(hash_val), filesize, str(self.__version),
                       "172.16.21.128:5000/get-app/temp_reader_v2"]
        self.__version += 1
        #print("Adding latest firmware update details to blockchain")
        self.block_chain_interaction()
        #print("Latest firmware update details added to blockchain")

    def add_latest_hash(self):

        self.__fcn = "addLatestFirmwareHash"
        self.__args = [str(self.__hash_str)]
        print("Adding the latest file hash to blockchain")
        self.block_chain_interaction()
        print("Latest file hash added to blockchain\n\n")

    def change_update_progress(self, status):
        self.__fcn = "changeUpdateProgress"
        self.__args = [self.__hash_str, self.__dev_id, "Downloading"]
        self.block_chain_interaction()

    def query_for_firmware(self):
        self.__fcn = "queryFirmware"
        self.__args = [self.__hash_str]
        response = self.block_chain_interaction()
        response_url = response["result"]["result"]["file_url"].split("/")
        return response_url

    def download_firmware(self, response_url):
        conn = http.client.HTTPConnection(response_url[0])
        download_result = "Completed"
        try:
            conn.request('GET', '/' + response_url[1] + '/' + response_url[2])

            response = conn.getresponse()
            # with open("calc_hash.py","w") as file_write:
            #    file_write.writelines(response.read().decode())
            with open("Downloads/" + response_url[2] + ".py", 'wb') as out_file:
                out_file.write(response.read())

        except http.client.IncompleteRead:
            download_result = "Interrupted"

        except Exception as e:
            print(e)
            download_result = "Something went wrong"

        finally:
            print(download_result)
            return download_result

if __name__ == "__main__":
    #range_list = [100, 200, 500]
    range_list = [500, 1000, 2000, 5000, 10000]
    dict_time_evals = {}
    csv_file = "Eval_results.csv"
    fileobj = open(csv_file, "a+")
    register_user()

    for i in range(0, 1000):
        start_time = time.time()
        filename = "temp_reader_v"+str(i)+".py"
        blockchain_interaction_obj = BlockchainInteractions()
        blockchain_interaction_obj.add_firmware_update(str("fdjfjgfdg"+str(i)), str("fsdfgdfgfdgd"+str(i)))
        time_diff = time.time() - start_time
        fileobj.write(str(i)+","+str(time_diff)+"\n")

    fileobj.close()
