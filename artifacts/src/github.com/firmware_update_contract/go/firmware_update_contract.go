package main

import (
	//"bytes"
	"encoding/json"
	"fmt"

	//"time"

	"github.com/hyperledger/fabric-chaincode-go/shim"
	sc "github.com/hyperledger/fabric-protos-go/peer"
	"github.com/hyperledger/fabric/common/flogging"
	//"github.com/hyperledger/fabric-chaincode-go/pkg/cid"
)

var latest_file_hash string

// SmartContract Define the Smart Contract structure
type SmartContract struct {
}

// Firmware :  Define the firmware structure, with 4 properties.  Structure tags are used by encoding/json library
type Firmware struct {
	Filename    string `json:"filename"`
	FileHash    string `json:"file_hash"`
	FileSize    string `json:"file_size"`
	FileVersion string `json:"file_version"`
	FileURL     string `json:"file_url"`
}

type FirmwareHash struct {
	FileHash string `json:"file_hash"`
}

type FirmwareLatestHash struct {
	FileHash string `json:"file_hash"`
}

type UpdateProgress struct {
	FileHash string `json:"file_hash"`
	DeviceID string `json:"device_ID"`
	Status   string `json:"status"`
}

type UpdateProgressStatus struct {
	Status string `json:"status"`
}

// Init ;  Method for initializing smart contract
func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) sc.Response {
	return shim.Success(nil)
}

var logger = flogging.MustGetLogger("firmware_update_contract_cc")

// Invoke :  Method for INVOKING smart contract
func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) sc.Response {

	function, args := APIstub.GetFunctionAndParameters()
	logger.Infof("Function name is:  %d", function)
	logger.Infof("Args length is : %d", len(args))

	switch function {
	case "addFirmwareUpdate":
		return s.addFirmwareUpdate(APIstub, args)
	case "addDeviceForUpdate":
		return s.addDeviceForUpdate(APIstub, args)
	case "changeUpdateProgress":
		return s.changeUpdateProgress(APIstub, args)
	case "queryFirmware":
		return s.queryFirmware(APIstub, args)
	case "compareFileHash":
		return s.compareFileHash(APIstub, args)
	case "addLatestFirmwareHash":
		return s.addLatestFirmwareHash(APIstub, args)
	case "getLatestFirmwareHash":
		return s.getLatestFirmwareHash(APIstub)
	case "getUpdateProgress":
		return s.getUpdateProgress(APIstub, args)
	case "initLedger":
		return s.initLedger(APIstub)

	default:
		return shim.Error("Invalid Smart Contract function name.")
	}

	// return shim.Error("Invalid Smart Contract function name.")

}
func (s *SmartContract) compareFileHash(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}
	return_hash := args[0]
	if latest_file_hash != args[0] {
		return_hash = latest_file_hash
	}
	var firmware_hash = FirmwareHash{FileHash: return_hash}
	firmwareHashAsBytes, _ := json.Marshal(firmware_hash)
	return shim.Success(firmwareHashAsBytes)
}

func (s *SmartContract) addLatestFirmwareHash(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	latestFirmwareAsBytes, _ := APIstub.GetState("latest_firmware")
	latestFirmware := FirmwareLatestHash{}

	json.Unmarshal(latestFirmwareAsBytes, &latestFirmware)
	latestFirmware.FileHash = args[0]

	latestFirmwareAsBytes, _ = json.Marshal(latestFirmware)
	APIstub.PutState("latest_firmware", latestFirmwareAsBytes)
	return shim.Success(latestFirmwareAsBytes)
}

func (s *SmartContract) getLatestFirmwareHash(APIstub shim.ChaincodeStubInterface) sc.Response {

	latestFirmwareAsBytes, _ := APIstub.GetState("latest_firmware")

	return shim.Success(latestFirmwareAsBytes)
}

func (s *SmartContract) queryFirmware(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	firmwareAsBytes, _ := APIstub.GetState("firmware_" + args[0])

	return shim.Success(firmwareAsBytes)
}

func (s *SmartContract) getUpdateProgress(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expecting 2")
	}

	updateProgressAsBytes, _ := APIstub.GetState("update_" + args[1] + "_" + args[0])
	updateProgress := UpdateProgress{}

	json.Unmarshal(updateProgressAsBytes, &updateProgress)
	var updateProgressStatus = UpdateProgressStatus{Status: updateProgress.Status}

	updateProgressStatusAsBytes, _ := json.Marshal(updateProgressStatus)

	return shim.Success(updateProgressStatusAsBytes)
}

func (s *SmartContract) addFirmwareUpdate(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 5 {
		return shim.Error("Incorrect number of arguments. Expecting 5")
	}

	var firmware = Firmware{Filename: args[0], FileHash: args[1], FileSize: args[2], FileVersion: args[3], FileURL: args[4]}
	latest_file_hash = args[1]

	firmwareAsBytes, _ := json.Marshal(firmware)
	APIstub.PutState("firmware_"+args[1], firmwareAsBytes)

	/*indexName := "owner~key"
	colorNameIndexKey, err := APIstub.CreateCompositeKey(indexName, []string{firmware.FileHash})
	if err != nil {
		return shim.Error(err.Error())
	}
	value := []byte{0x00}
	APIstub.PutState(colorNameIndexKey, value)*/

	return shim.Success(firmwareAsBytes)
}

func (s *SmartContract) addDeviceForUpdate(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 3 {
		return shim.Error("Incorrect number of arguments. Expecting 3")
	}

	var update = UpdateProgress{FileHash: args[0], DeviceID: args[1], Status: args[2]}

	updateAsBytes, _ := json.Marshal(update)
	APIstub.PutState("update_"+args[1]+"_"+args[0], updateAsBytes)

	return shim.Success(updateAsBytes)
}

func (s *SmartContract) initLedger(APIstub shim.ChaincodeStubInterface) sc.Response {
	firmwares := []Firmware{
		Firmware{Filename: "temp_reader_v2.py", FileHash: "e3477a6037d9e61fb4768ebc0bc222614cb4bb57cf37f9b3b569375a90b7b314", FileSize: "661kB", FileVersion: "1", FileURL: "172.16.21.128:5000/get-app/temp_reader_v2"},
		/*Car{Make: "Ford", Model: "Mustang", Colour: "red", Owner: "Brad"},
		Car{Make: "Hyundai", Model: "Tucson", Colour: "green", Owner: "Jin Soo"},
		Car{Make: "Volkswagen", Model: "Passat", Colour: "yellow", Owner: "Max"},
		Car{Make: "Tesla", Model: "S", Colour: "black", Owner: "Adriana"},
		Car{Make: "Peugeot", Model: "205", Colour: "purple", Owner: "Michel"},
		Car{Make: "Chery", Model: "S22L", Colour: "white", Owner: "Aarav"},
		Car{Make: "Fiat", Model: "Punto", Colour: "violet", Owner: "Pari"},
		Car{Make: "Tata", Model: "Nano", Colour: "indigo", Owner: "Valeria"},
		Car{Make: "Holden", Model: "Barina", Colour: "brown", Owner: "Shotaro"},*/}

	updateProgress := []UpdateProgress{
		UpdateProgress{FileHash: "e3477a6037d9e61fb4768ebc0bc222614cb4bb57cf37f9b3b569375a90b7b314", DeviceID: "Rpi1", Status: "In Progress"}}

	latestFirmware := []FirmwareLatestHash{
		FirmwareLatestHash{FileHash: "e3477a6037d9e61fb4768ebc0bc222614cb4bb57cf37f9b3b569375a90b7b314"}}

	i := 0
	for i < len(firmwares) {
		firmwareAsBytes, _ := json.Marshal(firmwares[i])
		APIstub.PutState("firmware_"+firmwares[i].FileHash, firmwareAsBytes)
		latest_file_hash = firmwares[i].FileHash
		//APIstub.PutState("firmware_"+strconv.Itoa(i), firmwareAsBytes)
		i = i + 1
	}

	i = 0
	for i < len(updateProgress) {
		updateProgressAsBytes, _ := json.Marshal(updateProgress[i])
		APIstub.PutState("update_"+updateProgress[i].DeviceID+"_"+updateProgress[i].FileHash, updateProgressAsBytes)
		//APIstub.PutState("update_"+strconv.Itoa(i), updateProgressAsBytes)
		i = i + 1
	}

	i = 0
	for i < len(latestFirmware) {
		latestFirmwareAsBytes, _ := json.Marshal(latestFirmware[i])
		APIstub.PutState("latest_firmware", latestFirmwareAsBytes)
		//APIstub.PutState("update_"+strconv.Itoa(i), updateProgressAsBytes)
		i = i + 1
	}
	return shim.Success(nil)
}

func (s *SmartContract) changeUpdateProgress(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 3 {
		return shim.Error("Incorrect number of arguments. Expecting 3")
	}

	updateProgressAsBytes, _ := APIstub.GetState("update_" + args[1] + "_" + args[0])
	updateProgress := UpdateProgress{}
	fmt.Printf("Error creating new Smart Contract: %s", updateProgress.FileHash)

	json.Unmarshal(updateProgressAsBytes, &updateProgress)
	updateProgress.Status = args[2]

	updateProgressAsBytes, _ = json.Marshal(updateProgress)
	APIstub.PutState("update_"+args[1]+"_"+args[0], updateProgressAsBytes)

	return shim.Success(updateProgressAsBytes)
}

// func (s *SmartContract) CreateCarAsset(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
// 	if len(args) != 1 {
// 		return shim.Error("Incorrect number of arguments. Expecting 1")
// 	}

// 	var car Car
// 	err := json.Unmarshal([]byte(args[0]), &car)
// 	if err != nil {
// 		return shim.Error(err.Error())
// 	}

// 	carAsBytes, err := json.Marshal(car)
// 	if err != nil {
// 		return shim.Error(err.Error())
// 	}

// 	err = APIstub.PutState(car.ID, carAsBytes)
// 	if err != nil {
// 		return shim.Error(err.Error())
// 	}

// 	return shim.Success(nil)
// }

// func (s *SmartContract) addBulkAsset(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
// 	logger.Infof("Function addBulkAsset called and length of arguments is:  %d", len(args))
// 	if len(args) >= 500 {
// 		logger.Errorf("Incorrect number of arguments in function CreateAsset, expecting less than 500, but got: %b", len(args))
// 		return shim.Error("Incorrect number of arguments, expecting 2")
// 	}

// 	var eventKeyValue []string

// 	for i, s := range args {

// 		key :=s[0];
// 		var car = Car{Make: s[1], Model: s[2], Colour: s[3], Owner: s[4]}

// 		eventKeyValue = strings.SplitN(s, "#", 3)
// 		if len(eventKeyValue) != 3 {
// 			logger.Errorf("Error occured, Please make sure that you have provided the array of strings and each string should be  in \"EventType#Key#Value\" format")
// 			return shim.Error("Error occured, Please make sure that you have provided the array of strings and each string should be  in \"EventType#Key#Value\" format")
// 		}

// 		assetAsBytes := []byte(eventKeyValue[2])
// 		err := APIstub.PutState(eventKeyValue[1], assetAsBytes)
// 		if err != nil {
// 			logger.Errorf("Error coocured while putting state for asset %s in APIStub, error: %s", eventKeyValue[1], err.Error())
// 			return shim.Error(err.Error())
// 		}
// 		// logger.infof("Adding value for ")
// 		fmt.Println(i, s)

// 		indexName := "Event~Id"
// 		eventAndIDIndexKey, err2 := APIstub.CreateCompositeKey(indexName, []string{eventKeyValue[0], eventKeyValue[1]})

// 		if err2 != nil {
// 			logger.Errorf("Error coocured while putting state in APIStub, error: %s", err.Error())
// 			return shim.Error(err2.Error())
// 		}

// 		value := []byte{0x00}
// 		err = APIstub.PutState(eventAndIDIndexKey, value)
// 		if err != nil {
// 			logger.Errorf("Error coocured while putting state in APIStub, error: %s", err.Error())
// 			return shim.Error(err.Error())
// 		}
// 		// logger.Infof("Created Composite key : %s", eventAndIDIndexKey)

// 	}

// 	return shim.Success(nil)
// }

// The main function is only relevant in unit test mode. Only included here for completeness.
func main() {

	// Create a new Smart Contract
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating new Smart Contract: %s", err)
	}
}
