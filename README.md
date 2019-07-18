# sync-ad-to-everbridge
Reads a Azure AD Group and inserts Everbridge Contacts into the selected Everbridge Group <br/>
Requires a Azure Application that has permissions to read Groups(Requires Admin Consent)

# How to install
pip -r requirements.txt

# How to test
cd tests <br/>
pytest

# How to run
python /sync_ad_to_everbridge/sync_ad_to_everbridge.py /config/config.json
# config.json format
{ <br/>
	"clientId":"", <br/>
	"clientSecret":"", <br/>
	"everbridgeUsername":"", <br/>
	"everbridgePassword":"", <br/>
	"everbridgeOrg":"", <br/>
	"everbridgeGroup":"", <br/>
	"adTenant":"", <br/>
	"adGroupId":"", <br/>
	"adGroupName":"" <br/>
}