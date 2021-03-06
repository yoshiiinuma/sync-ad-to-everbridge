# sync-ad-to-everbridge
Reads a Azure AD Group and inserts Everbridge Contacts into the selected Everbridge Group
Requires a Azure Application that has permissions to read Groups(Requires Admin Consent)

# How to install (new)
```bash
$ pip install pipenv
$ cd sync-ad-to-everbridge
$ pipenv install --dev
```

# How to generate requirements.txt
```bash
# For Production
$ pipenv lock -r > requirements.txt

# For development
$ pipenv run pip freeze > requirements.txt
```

# How to set up the application running environment
```bash
# Run this command before running the app or tests
$ pipenv shell
```

# How to test
```bash
$ pipenv shell
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
1. Install  Azure Functions Core Tools ([Instructions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools))
```bash
# For Windows
$ npm install -g azure-functions-core-tools
```

2. Install Azure CLI ([Instructions](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest))

3. Get the Azure Free Subscription

4. Install and run Docker

5. Copy the pipfile.lock into the EverbridgeHttp Folder

6. Copy the api files into the EverbridgeTest Folder

7. Copy the config file into the EverbrideTest Folder

8. Execute the Generate_Requirements.sh

9. From your EverbridgeHttp folder, enter in these commands
```bash
$ az login
$ az group create --name <myResourceGroup> --location westus
$ az storage account create --name <storage_name> --location westus --resource-group <myResourceGroup> --sku Standard_LRS
$ az functionapp create --resource-group <myResourceGroup> --os-type Linux --consumption-plan-location westus  --runtime python --name <APP_NAME> --storage-account  <storage_name>
$ func azure functionapp publish <APP_NAME> --build-native-deps --force
```
```bash
# To run locally
$ pipenv shell
$ pipenv install
$ func start host
```

# config.json format
```json
{
  "clientId":"Azure AD Client ID",
  "clientSecret":"Azure AD Client Secret",
  "everbridgeUsername":"EverBridge User Name",
  "everbridgePassword":"EverBridge Password",
  "everbridgeOrg":"EverBridge Org",
  "adTenant":"Azure AD Tenant",
  "adGroupId":["Azure AD Group ID1","Azure AD Group ID2"],
	"logFileName":"logfile.txt",
	"logLevel":"DEBUG|INFO|WARNING|ERROR"
}
```
