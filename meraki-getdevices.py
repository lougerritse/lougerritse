#MIT License
#
#Copyright (c) 2020 Cisco Systems, Inc. and/or its affiliates  #
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
# Original version of this file was found at the following link.
# https://github.com/meraki/dashboard-api-python/blob/master/examples/org_wide_clients_v1.py
# my modifications include steps to configure the client side.
# info from Meraki available here --> https://developer.cisco.com/meraki/api-v1/#!introduction
# 1. install python (3.9.6) available at current secure version
# - -recommended to update path and install for all users - customize install and place python folder to your preference.
##### https://www.python.org/downloads/release/python-396/
# 2. after install open command line and execute [pip install --upgrade meraki]
# 3. copy the code below into a python file perhaps getmkdevices.py
# 4. gather the API_KEY from the dashboard and insert the key into the api_key variable.
# 4. execute python getmkdevices.py and watch the data collection.
# How to get the API key?
# Login to the dashboard. Organization --> Settings
# Enable the API feature in the dashboard api access section.
# Follow the link to your profile and generate an API key.
# End of comments & License section
# Lou Gerritse 
######################################################################################################################################################################


import csv

from datetime import datetime
import os

import meraki

# Either input your API key below by uncommenting line 10 and changing line 16 to api_key=API_KEY,
# or set an environment variable (preferred) to define your API key. The former is insecure and not recommended.
# For example, in Linux/macOS:  export MERAKI_DASHBOARD_API_KEY=093b24e85df15a3e66f1fc359f4c48493eaa1b73
# API_KEY = '093b24e85df15a3e66f1fc359f4c48493eaa1b73'

def main():
    # Instantiate a Meraki dashboard API session
    dashboard = meraki.DashboardAPI(
        api_key='',
        base_url='https://api.meraki.com/api/v1/',
        output_log=True,
        log_file_prefix=os.path.basename(__file__)[:-3],
        log_path='',
        print_console=False
    )

    # Get list of organizations to which API key has access
    organizations = dashboard.organizations.getOrganizations()
    
    # Iterate through list of orgs
    for org in organizations:
        print(f'\nAnalyzing organization {org["name"]}:')
        org_id = org['id']

        # Get list of networks in organization
        try:
            networks = dashboard.organizations.getOrganizationNetworks(org_id)
        except meraki.APIError as e:
            print(f'Meraki API error: {e}')
            print(f'status code = {e.status}')
            print(f'reason = {e.reason}')
            print(f'error = {e.message}')
            continue
        except Exception as e:
            print(f'some other error: {e}')
            continue
        
        # Create local folder
        todays_date = f'{datetime.now():%Y-%m-%d}'
        folder_name = f'Org {org_id} clients {todays_date}'
        if folder_name not in os.listdir():
            os.mkdir(folder_name)

        # Iterate through networks
        total = len(networks)
        counter = 1
        print(f'  - iterating through {total} networks in organization {org_id}')
        for net in networks:
            print(f'Finding clients in network {net["name"]} ({counter} of {total})')
            try:
                # Get list of clients on network, filtering on timespan of last 14 days
                clients = dashboard.networks.getNetworkClients(net['id'], timespan=60*60*24*14, perPage=1000, total_pages='all')
            except meraki.APIError as e:
                print(f'Meraki API error: {e}')
                print(f'status code = {e.status}')
                print(f'reason = {e.reason}')
                print(f'error = {e.message}')
            except Exception as e:
                print(f'some other error: {e}')
            else:
                if clients:
                    # Write to file
                    file_name = f'{net["name"]}.csv'
                    output_file = open(f'{folder_name}/{file_name}', mode='w', newline='\n')
                    field_names = clients[0].keys()
                    csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"',
                                                quoting=csv.QUOTE_ALL)
                    csv_writer.writeheader()
                    csv_writer.writerows(clients)
                    output_file.close()
                    print(f'  - found {len(clients)}')

            counter += 1

        # Stitch together one consolidated CSV per org
        output_file = open(f'{folder_name}.csv', mode='w', newline='\n')
        field_names = ['id', 'mac', 'description', 'ip', 'ip6', 'ip6Local', 'user', 'firstSeen', 'lastSeen', 'manufacturer', 'os', 'recentDeviceSerial', 'recentDeviceName', 'recentDeviceMac', 'ssid', 'vlan', 'switchport', 'usage', 'status', 'notes', 'smInstalled', 'groupPolicy8021x','deviceTypePrediction', 'recentDeviceConnection', 'adaptivePolicyGroup']
        field_names.insert(0, "Network Name")
        field_names.insert(1, "Network ID")
    
        csv_writer = csv.DictWriter(output_file, field_names, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writeheader()
        for net in networks:
            file_name = f'{net["name"]}.csv'
            if file_name in os.listdir(folder_name):
                with open(f'{folder_name}/{file_name}') as input_file:
                    csv_reader = csv.DictReader(input_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                    next(csv_reader)
                    for row in csv_reader:
                        row['Network Name'] = net['name']
                        row['Network ID'] = net['id']
                        csv_writer.writerow(row)


if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f'\nScript complete, total runtime {end_time - start_time}')
