import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('cloudtrail')

    response = client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'DescribeLogStreams'
            },
        ],
    )

    accessed_users = set()
    for event in response['Events']:
        username = event['Username']
        accessed_users.add(username)

    return {
        'statusCode': 200,
        'body': json.dumps(list(accessed_users))
    }