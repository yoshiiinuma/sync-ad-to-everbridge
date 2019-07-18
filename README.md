# sync-ad-to-everbridge
Reads a Azure AD Group and inserts Everbridge Contacts into the selected Everbridge Group
Requires a Azure Application that has permissions to read Groups(Requires Admin Consent)

# How to install
pip -r requirements.txt

#How to test
cd tests
pytest

#config.json format
{
	"clientId":"",
	"clientSecret":"",
	"everbridgeUsername":"",
	"everbridgePassword":"",
	"everbridgeOrg":"",
	"everbridgeGroup":"",
	"adTenant":"",
	"adGroupId":"",
	"adGroupName":""
}