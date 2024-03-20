import boto3
from datetime import datetime, timedelta

def get_users_in_cognito_groups(user_pool_id):
    client = boto3.client('cognito-idp')

    # Get all groups in the user pool
    response = client.list_groups(UserPoolId=user_pool_id)
    groups = response['Groups']

    users_in_groups = {}

    # For each group, get all users
    for group in groups:
        group_name = group['GroupName']
        response = client.list_users_in_group(UserPoolId=user_pool_id, GroupName=group_name)

        # Add the users to the result
        users_in_groups[group_name] = [(user['Username'], user['UserAttributes']) for user in response['Users']]

    return users_in_groups

def get_cloudwatch_logs_access():
    client = boto3.client('cloudtrail')

    # Get the time 24 hours ago
    start_time = datetime.now() - timedelta(days=1)

    # Get all events in the last 24 hours
    response = client.lookup_events(StartTime=start_time)

    # Filter events for logs.amazonaws.com and specific EventNames
    relevant_events = []
    for event in response['Events']:
        if event['EventSource'] == 'logs.amazonaws.com' and event['EventName'] in ['GetLogEvents', 'DescribeLogStreams']:
            relevant_events.append(event)

    return relevant_events

def get_grouped_user_events(user_pool_id):
    # Get all users in each group
    users_in_groups = get_users_in_cognito_groups(user_pool_id)

    # Get all relevant events
    events = get_cloudwatch_logs_access()

    # Group events by user
    events_by_user = {}
    for event in events:
        username = event['Username']
        if username not in events_by_user:
            events_by_user[username] = []
        events_by_user[username].append(event)

    # Group users and their events by group
    events_by_group = {}
    for group, users in users_in_groups.items():
        for user in users:
            username = user[0]
            if username in events_by_user:
                if group not in events_by_group:
                    events_by_group[group] = {}
                events_by_group[group][username] = events_by_user[username]

    return events_by_group