import threading
import http.client
import json
import time
import logging

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

class BlockchainInteractions(threading.Thread):
    def __init__(self):
        self.__fcn = ""
        self.__args = ""
        self.__dev_id = "RPi2"
        self.__hash_str = "f68869d27d5010f04ca6aa89a6c7061ecc22721ee2f8d8b0a1c256974c2ad90c"
        self.__version = 1
        self.exception = None
        threading.Thread.__init__(self)

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

        conn_blk_chain.request('POST', '/channels/mychannel/chaincodes/firmware_update_contract', json_data,
                               headers)

        response = conn_blk_chain.getresponse()

        resp_str = json.loads(response.read().decode())
        conn_blk_chain.close()
        return resp_str

    def block_chain_interaction_get(self):
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
        #json_data = json.dumps(foo)

        conn_blk_chain.request('GET', '/channels/mychannel/chaincodes/firmware_update_contract?fcn=getLatestFirmwareHash&peers=["peer0.org1.firmwareupdate.com","peer0.org2.firmwareupdate.com"]&chaincodeName=firmware_update_contract&channelName=mychannel&args=[]',
                               headers=headers)

        response = conn_blk_chain.getresponse()

        resp_str = json.loads(response.read().decode())
        conn_blk_chain.close()
        return resp_str

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

    def check_for_latest_update(self):
        print("Checking for latest update")
        self.__fcn = "getLatestFirmwareHash"
        self.__args = []
        return_val = [self.__hash_str, False]
        resp = self.block_chain_interaction_get()
        print(repr(resp))
        resp_hash = resp["result"]["file_hash"]
        if self.__hash_str != resp_hash:
            self.__hash_str = resp_hash
            print("\n\nNew Hash with value " + resp_hash + " available ==> Newer Firmware Update available")
            return_val = [resp_hash, True]

        return return_val

    def run(self):
        try:
            self.check_for_latest_update()
        except Exception as e:
            self.exception=e


def print_hello():
    print("hello")

register_user()
blockchain_interaction_obj = BlockchainInteractions()
threads = list()
start_time = time.time()
range_list = []
csv_file = "Eval_results_parallel.csv"
fileobj = open(csv_file, "a+")
range_list=[1,2,3,4]

#for vals in range(5, 76, 5):
range_list.extend(range(5, 76, 5))


for each_range in range_list:
    start_time = time.time()
    for index in range(0, each_range):
        logging.info("Main    : create and start thread %d.", index)
        x = blockchain_interaction_obj = BlockchainInteractions()
        threads.append(x)
        x.start()
    for thread in threads:
            # join() is used to synchronize threads
            # Calling join() on a thread makes the parent thread wait
            # until the child thread has finished
        thread.join()
        if thread.exception is not None:
            raise thread.exception

    time_diff = time.time() - start_time
    print("Main thread exiting... Total time: " + str(time_diff))
    fileobj.write(str(each_range)+","+str(time_diff)+"\n")

fileobj.close()