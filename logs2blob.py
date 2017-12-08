import adal
import requests
import json
import csv
import datetime
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
import datetime
from azure.common.credentials import ServicePrincipalCredentials
import automationassets

tmpfile = "/tmp/logs.csv"

# LogAnalytics init
# Details of query.  Modify these to your requirements.
query = "Type=\"Syslog\" TimeGenerated>NOW-12HOURS"
end_time = datetime.datetime.utcnow()
start_time = end_time - datetime.timedelta(hours=24)
num_results = 10000  # If not provided, a default of 10 results will be used.

# Get access token 
context = adal.AuthenticationContext('https://login.microsoftonline.com/' + automationassets.get_automation_variable("tenant_id"))      
token_response = context.acquire_token_with_client_credentials('https://management.core.windows.net/', automationassets.get_automation_variable("application_id"), automationassets.get_automation_variable("application_key"))
access_token = token_response.get('accessToken')                                                                                       
                                                                                                                                       
# Add token to header                                                                                                                  
headers = {                                                                                                                            
    "Authorization": 'Bearer ' + access_token,                                                                                         
    "Content-Type":'application/json'                                                                                                  
}                                                                                                                                      

# Build search parameters from query details
search_params = {
        "query": query,
        "top": num_results
        }
                                                                                                                                       
# Blob init                                                                                                                            
block_blob_service = BlockBlobService(account_name=automationassets.get_automation_variable("blobservicename"), account_key=automationassets.get_automation_variable("blobstorage-key"))

                                                                                                                                                                          
#  Oms init                                                                                                                                                                
uri_base = 'https://management.azure.com'                                                                                                                                 
uri_api = 'api-version=2015-11-01-preview'                                                                                                                                
uri_subscription = 'https://management.azure.com/subscriptions/' + automationassets.get_automation_variable("subscription_id") 
uri_resourcegroup = uri_subscription + '/resourcegroups/'+ automationassets.get_automation_variable("resource_group") 
uri_workspace = uri_resourcegroup + '/providers/Microsoft.OperationalInsights/workspaces/' + automationassets.get_automation_variable("workspace") 
uri_search = uri_workspace + '/search'                                                                                                                                    
                                                                                                                                                                          

def getDataFromLogAnalytics():                                                                                                                                            
                                                                                                                                                                          
    # Build URL and send post request                                                                                                                                     
    uri = uri_search + '?' + uri_api                                                                                                                                      
    response = requests.post(uri,json=search_params,headers=headers)                                                                                                      
                                                                                                                                                                          
    # Response of 200 if successful                                                                                                                                       
    if response.status_code == 200:                                                                                                                                       
        data = response.json()                                                                                                                                            
        status = data["__metadata"]["Status"]                                                                                                                             
                                                                                                                                                                          
    # Convert to json obj                                                                                                                                                 
    json_data = json.dumps(data["value"])                                                                                                                                 
    json_parsed = json.loads(json_data)                                                                                                                                   
                                                                                                                                                                          
    try:                                                                                                                                                                  
        log_data = open(tmpfile, 'w')                                                                                                                             
        csvwriter = csv.writer(log_data)                                                                                                                                  
        for index in range(len(json_parsed)):                                                                                                                             
            log_entry = json_parsed[index]                                                                                                                                
            expected_msg = log_entry['HostIP'],log_entry['SeverityLevel'],log_entry['SyslogMessage']                                                                      
            csvwriter.writerow(expected_msg)                                                                                                                              
    except:                                                                                                                                                               
        print 'exception writing file'                                                                                                                                
    finally:                                                                                                                                                              
        log_data.close()                                                                                                                                                  
                                                                                                                                                                          
                                                                                                                                                                          
def persistToBlobStorage(localFilename,remoteFilename):                                                                                                                   
                                                                                                                                                                          
    block_blob_service.create_blob_from_path(                                                                                                                             
        'logging',                                                                                                                                                        
        remoteFilename,                                                                                                                                                   
        localFilename,                                                                                                                                                    
        content_settings=ContentSettings(content_type='text/csv')                                                                                                         
    )


if __name__ == "__main__":                                                                                                                                                
    getDataFromLogAnalytics()                                                                                                                                             
    persistToBlobStorage(tmpfile,'logging-'+str(datetime.datetime.utcnow()))   
