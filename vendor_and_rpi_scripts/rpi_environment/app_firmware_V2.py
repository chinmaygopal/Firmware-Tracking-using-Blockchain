import http.client
import json
import socket
import subprocess
import time
import hashlib

BUF_SIZE = 65536  # lets read stuff in 64kb chunk
conn_blk_chain = http.client.HTTPConnection("localhost:4000")
token = ""
app_process = ""

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

def register_user():
    headers = {'Content-type': 'application/json'}
    foo = {
            "username": "chinmay2",
            "orgName": "Org1"
    }
    json_data = json.dumps(foo)
    conn_blk_chain.request('POST', '/users', json_data, headers)
    response = conn_blk_chain.getresponse()
    global token
    token = json.loads(response.read().decode())["token"]

def calc_hash(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()

class FileOps:
    def __init__(self, filename):
        self.__filename = filename


    def rewrite_app(self):
        cmd =  "mv " + self.__filename+" Backup/"+self.__filename
        p = subprocess.Popen(cmd.split())
        time.sleep(5)

        cmd = "rm nohup.out"
        p = subprocess.Popen(cmd.split())
        time.sleep(5)

        cmd =  "mv Downloads/" + self.__filename+" "+self.__filename
        p = subprocess.Popen(cmd.split())
        print(self.__filename+" is successfully installed and is at the newest version.")
        time.sleep(10)

    def restore_last_version(self):
        print("Restoring to last working version...")
        cmd = "cp Backup/" + self.__filename + " " + self.__filename
        p = subprocess.Popen(cmd.split())
        time.sleep(5)
        print("Rollback complete.")

    def move_to_incorrect_hash(self):
        print("Moving file to Incorrect Hash..")
        cmd = "mv Downloads/" + self.__filename + " IncorrectHash/" + self.__filename
        p = subprocess.Popen(cmd.split())
        time.sleep(5)
        print("Move complete.")

    def start_process(self):
        global app_process
        # start app
        cmd = "nohup python3 "+self.__filename
        app_process = subprocess.Popen(cmd.split())
        print("Process "+self.__filename+" started ...\n\n")
        time.sleep(3)


    def terminate_process(self):
        global app_process
        # start app
        cmd = "kill " + str(app_process.pid)
        p = subprocess.Popen(cmd.split())
        app_process.terminate()
        print("Process "+self.__filename+" has been terminated ...")
        time.sleep(3)



class BlockchainInteractions:

    def __init__(self):
        self.__fcn = ""
        self.__args = ""
        self.__dev_id = str(getserial())
        self.__filename = "temp_reader_v2.py"
        self.__hash_str = str(calc_hash(self.__filename))

    def set_fcn(self,fcn):
        self.__fcn = fcn

    def set_args(self,args):
        self.__args = args

    def set_hash(self,hash_val):
        self.__hash_str = hash_val

    def get_filename(self):
        return self.__filename

    def get_device_id(self):
        return self.__dev_id

    def block_chain_interaction(self):
        global token

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
        not_request_serviced = True
        while not_request_serviced:
            try:
                conn_blk_chain.request('POST', '/channels/mychannel/chaincodes/firmware_update_contract', json_data, headers)
                response = conn_blk_chain.getresponse()
                not_request_serviced = False
            except BrokenPipeError:
                pass
            except http.client.CannotSendRequest:
                pass

        return json.loads(response.read().decode())

    def check_for_latest_update(self):
        print("Checking for latest update")
        self.__fcn = "getLatestFirmwareHash"
        self.__args = []
        return_val = [self.__hash_str, False]
        resp = self.block_chain_interaction()
        if len(resp["result"]) == 2:
            resp_hash = resp["result"]["result"]["file_hash"]
            if self.__hash_str != resp_hash:
                self.__hash_str = resp_hash
                print("\n\nNew Hash with value "+resp_hash+" available ==> Newer Firmware Update available")
                return_val = [resp_hash, True]
        else:
            time.sleep(3)

        return return_val

    def add_device_for_update(self):
        print("Adding device to blockchain "+self.__dev_id+" for tracking update progress")
        self.__fcn = "addDeviceForUpdate"
        self.__args = [self.__hash_str, self.__dev_id, "Started"]
        self.block_chain_interaction()

    def change_update_progress(self, status_val):
        self.__fcn = "changeUpdateProgress"
        print("Changed status "+ str(status_val))
        self.__args = [self.__hash_str, self.__dev_id, status_val]
        self.block_chain_interaction()

    def query_for_firmware(self):
        print("Fetching latest firmware details from blockchain")
        self.__fcn = "queryFirmware"
        self.__args = [self.__hash_str]
        response = self.block_chain_interaction()
        response_url = response["result"]["result"]["file_url"].split("/")
        return response_url


    def download_firmware(self, response_url):
        print("Downloading Firmware from "+ response_url[0])
        conn = http.client.HTTPConnection(response_url[0])
        download_result = "Completed"
        try:
            conn.request('GET', '/' + response_url[1] + '/' + response_url[2])

            response = conn.getresponse()

            with open("Downloads/"+response_url[2] + ".py", 'wb') as out_file:
                out_file.write(response.read())
            print("Firmware downloaded successfully!")

        except http.client.IncompleteRead:
            download_result = "Download Interrupted"

        except Exception as e:
            print(e)
            download_result = "Something went wrong"

        finally:
            print(download_result)
            return download_result

    def compare_hash(self):
        calc_hash_str = calc_hash("Downloads/"+self.__filename)
        return_val = True
        # calc_hash_str = "1234"
        if calc_hash_str != self.__hash_str:
            print("Calculated hash is: "+str(calc_hash_str))
            return_val = False

        return return_val

if __name__ == '__main__':

    register_user()
    blockchain_interaction_obj = BlockchainInteractions()
    filename = blockchain_interaction_obj.get_filename()
    fileop_obj = FileOps(filename)

    fileop_obj.start_process()

    while True:
        update_resp = blockchain_interaction_obj.check_for_latest_update()
        if update_resp[1]:
            blockchain_interaction_obj.add_device_for_update()

            response_url = blockchain_interaction_obj.query_for_firmware()

            status = "Downloading"
            blockchain_interaction_obj.change_update_progress(status)

            download_result = blockchain_interaction_obj.download_firmware(response_url)


            if download_result == "Completed":

                conn_blk_chain.close()
                conn_blk_chain = ""
                try:
                    if blockchain_interaction_obj.compare_hash():
                        s = socket.socket()
                        print("Socket successfully created")
                        port = 12345
                        s.bind(('127.0.0.1', port))
                        print("socket binded to %s" % (port))
                        s.listen(5)
                        print("Socket is listening for " + filename + " to stop")

                        # wait for app to reach safe completion state
                        # Establish connection with client.
                        c, addr = s.accept()
                        print("Received connection from " + blockchain_interaction_obj.get_filename())

                        # Close the connection with the client
                        c.close()
                        fileop_obj.terminate_process()
                        fileop_obj.rewrite_app()
                        fileop_obj.start_process()
                        status = "Installation Successful"


                    else:
                        print("Incorrect file downloaded! Please check!")
                        status = "Firmware hash mismatch"
                        fileop_obj.move_to_incorrect_hash()
                        # fileop_obj.restore_last_version()


                    conn_blk_chain = http.client.HTTPConnection("localhost:4000")

                except Exception as e:
                    print(e)

            else:
                status = "Download Interrupted"

            print(status)
            blockchain_interaction_obj.change_update_progress(status)
            hash_val = str(calc_hash(filename))
            print("Set hash to "+ hash_val+"\n\n")
            blockchain_interaction_obj.set_hash(hash_val)


