# sync-ad-to-everbridge
Reads a Azure AD Group and inserts Everbridge Contacts into the selected Everbridge Group 
Requires a Azure Application that has permissions to read Groups(Requires Admin Consent)

# How to install
```bash
$ pip -r requirements.txt 
```
# How to install (new)
```bash
$ pip install pipenv
$ cd sync-ad-to-everbridge
$ pipenv install
```
# How to test
```bash
$ pytest
```
# How to run
```bash
$ pipenv shell
$ python bin/main.py config/config.json
```
# How to use pylint
```bash
$ pipenv shell
$ pylint path-to-file
```
# How to deploy to Azure Functions
1 - Install  Azure Functions Core Tools

2 - Install Azure CLI

3 - Get the Azure Free Subscription

4 - Install and run Docker

4 - Copy the pipfile.lock into the EverbridgeHttp Folder

5 - Copy the api files into the EverbridgeTest Folder

6 - Copy the config file into the EverbrideTest Folder

7 - From your EverbridgeHttp folder, enter in these commands
```bash
az login
az group create --name <myResourceGroup> --location westus
az storage account create --name <storage_name> --location westus --resource-group <myResourceGroup> --sku Standard_LRS
az functionapp create --resource-group <myResourceGroup> --os-type Linux --consumption-plan-location westus  --runtime python --name <APP_NAME> --storage-account  <storage_name>
func azure functionapp publish <APP_NAME> --build-native-deps --force
```

To run locally

```bash
pipenv shell
pipenv install
func start host
```
# config.json format
```json
{ 
	"clientId":"", 
	"clientSecret":"", 
	"everbridgeUsername":"", 
	"everbridgePassword":"", 
	"everbridgeOrg":"", 
	"everbridgeGroup":"", 
	"adTenant":"", 
	"adGroupId":"", 
	"adGroupName":"", 
	"logFileName":""
}
```
