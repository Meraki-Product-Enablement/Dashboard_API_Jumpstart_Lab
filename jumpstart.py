import meraki
import logging

# ********** Lab step 6 **********
# Replace with your Merak Dashboard API key
# Note, in production, it is recommended to use an environment variable to store the API key
API_KEY = 'YourAPIKey'

# Replace with the provided lab organization ID
# Please DON'T put any production Meraki organization ID to this variable
LAB_ORG_ID = 'YourLabOrgID'

# Initialize variables for branch and campus networks
BRANCH_NW = None
CAMPUS_NW = None

# Other global variables
SEPARATOR = '=' * 50

# ********** Lab step 7 **********
# Create a Meraki Dashboard API session instance
DASHBOARD = meraki.DashboardAPI(
    api_key=API_KEY,
)

# Set Meraki SDK logger to INFO level (hides DEBUG logs)
logging.getLogger('meraki').setLevel(logging.INFO)

# Get a list of networks in the organization and set the branch and campus network IDs
# Use try-except to handle API errors
print(SEPARATOR)
try: 
    print(f"Getting network list and setting the branch and campus network IDs")
    networks = DASHBOARD.organizations.getOrganizationNetworks(organizationId=LAB_ORG_ID)
    for network in networks:
        if 'branch' in network['name'].lower():
            BRANCH_NW = network
        elif 'campus' in network['name'].lower():
            CAMPUS_NW = network
        print(f"Network ID: {network['id']}, Name: {network['name']}")
except meraki.APIError as e:
    print(f"Meraki API Error: {e}\n")
    exit()

# ********** Lab step 8 & 9 **********
# Update campus network name to 'Python-Campus'
print(SEPARATOR)
try:
    if CAMPUS_NW['name'] != 'Python-Campus':
        print(f"Updating Campus network name to 'Python-Campus'")
        result =  DASHBOARD.networks.updateNetwork(networkId=CAMPUS_NW['id'], name='Python-Campus')  
        if result == None:
            print("Nothing happend because the simulation mode is enabled.")
            print("➡️➡️ Next step: Change the simulate paraemter to False and run the script agian.\n")
            exit()
        else:
            print(f"Network name was successfully updated to \'Python-Campus\'.\n")
    else:
        print(f"The campus network name is already 'Python-Campus'.\nReady for the next lab step.\n")
except meraki.APIError as e:
    print(f"Meraki API Error: {e}")
    exit()

# ********** Lab step 10 **********
# Update swith port settings and rename campus switch
print(SEPARATOR)
try:
    print(f"Assign the port#2 of the campus switch to the VLAN 99.")
    campus_switches = DASHBOARD.organizations.getOrganizationDevices(organizationId=LAB_ORG_ID,networkIds=[CAMPUS_NW['id']],productTypes=['switch'])
    if campus_switches == []:
        print("No switch found in the campus network.")
        exit()
    DASHBOARD.devices.updateDevice(serial=campus_switches[0]['serial'],name='Campus-Switch')
    port_config = {}
    port_config = {'name': 'To-Campus-AP', 'allowdVlans' : '10-200', 'tags': ['wireless','meetingroom']}
    result = DASHBOARD.switch.updateDeviceSwitchPort(serial=campus_switches[0]['serial'],portId='2',**port_config)
    if result != None:
        print("Port configuration was successfully updated.\nReady for the next lab step.\n")
except meraki.APIError as e:
    print(f"Meraki API Error: {e}")
    print("➡️➡️ Next step: Follow the lab guide to fix the API call. Then run the script agian.\n")
    exit()

# ********** Lab step 11 **********
# Configure two SSIDs: corp and guest
print(SEPARATOR)
try:
    print(f"Rename APs in the campus network.")
    campus_aps = DASHBOARD.organizations.getOrganizationDevices(organizationId=LAB_ORG_ID,networkIds=[CAMPUS_NW['id']],productTypes=['wireless'])
    for ap in campus_aps:
        DASHBOARD.devices.updateDevice(serial=ap['serial'],name='Campus-AP-'+ ap['mac'][-5:-4] + ap['mac'][-2:])
    print(f"Configure two SSIDs in the campus network: corp and guest")
    ssids = [{ 'number': 0, 'settings':{'name': 'Jumpstart-corp', 'enabled': True, 'authMode':'8021x-meraki','wpaEncryptionMode':'WPA2 only','ipAssignmentMode':'Bridge mode','useVlanTagging':True,'defaultVlanId':99}},
             {'number': 1, 'settings':{'name': 'Jumpstart-guest', 'enabled': True, 'authMode':'psk','encryptionMode':'wpa','psk':'jumpstart1234'}}]
    for ssid in ssids:
        DASHBOARD.wireless.updateNetworkWirelessSsid(networkId=CAMPUS_NW['id'],number=ssid['number'],**ssid['settings'])
    print('You are now at the end of Meraki Python SDK lab.')

except meraki.APIError as e:
    print(f"Meraki API Error: {e}")
    exit()

# End of the script