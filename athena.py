import boto3
import time

# Initialize Boto3 Athena client
athena_client = boto3.client('athena', region_name='your-region')

# Define the SQL query
sql_query = """
SELECT
    eventtime,
    eventname,
    sourceipaddress,
    useridentity.arn,
    useridentity.username,
    requestparameters,
    responseelements
FROM
    your_cloudtrail_logs_table_name
WHERE
    eventsource = 'logs.amazonaws.com'
    AND useridentity.arn LIKE '%your-cognito-role-name/cognito-username%'
ORDER BY
    eventtime DESC;
"""

# Define the Athena query execution parameters
query_execution_params = {
    'QueryString': sql_query,
    'QueryExecutionContext': {
        'Database': 'your_athena_database_name'
    },
    'ResultConfiguration': {
        'OutputLocation': 's3://your-query-results-bucket/path/'
    }
}

# Start the query execution
query_execution_response = athena_client.start_query_execution(**query_execution_params)
query_execution_id = query_execution_response['QueryExecutionId']

# Wait for the query to complete
query_status = None
while query_status != 'SUCCEEDED':
    query_execution = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
    query_status = query_execution['QueryExecution']['Status']['State']
    
    if query_status in ['FAILED', 'CANCELLED']:
        raise Exception("Athena query failed or was cancelled")
    
    time.sleep(1)  # Poll every second

# Fetch the query results
query_results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)

# Process query results
for row in query_results_response['ResultSet']['Rows']:
    print(row)  # Process each row as needed
