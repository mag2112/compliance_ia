import boto3
from requests_aws4auth import AWS4Auth
import requests
import json

region = 'us-east-2'
service = 'es'
host = 'vpc-compliance-opensearch-6pwgiyup25lkp32dorw4hq2n34.us-east-2.es.amazonaws.com'

session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# Endpoint da role mapping
url = f"https://{host}/_plugins/_security/api/rolesmapping/all_access"

response = requests.get(url, auth=awsauth, verify=False)

print("Status:", response.status_code)
print("Resposta:")
print(json.dumps(response.json(), indent=2))
