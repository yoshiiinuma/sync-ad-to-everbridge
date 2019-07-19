# sync-ad-to-everbridge
Reads a Azure AD Group and inserts Everbridge Contacts into the selected Everbridge Group <br/>
Requires a Azure Application that has permissions to read Groups(Requires Admin Consent)

# How to install
```bash
$ pip -r requirements.txt <br/>
$ mkdir logs <br/>
$ mkdir config <br/>
$ touch config/config.json <br/>
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
# config.json format
```json
{ <br/>
	"clientId":"", <br/>
	"clientSecret":"", <br/>
	"everbridgeUsername":"", <br/>
	"everbridgePassword":"", <br/>
	"everbridgeOrg":"", <br/>
	"everbridgeGroup":"", <br/>
	"adTenant":"", <br/>
	"adGroupId":"", <br/>
	"adGroupName":"", <br/>
	"logFileName":""
}
```
