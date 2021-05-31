import boto3
import pandas as pd
import io
import re
import time

BUCKET = 'aws-athena-query-results-697036326133-us-east-2'
S3_PATH = 'testes-matheus-waze'

def _make_params(query):
    return {
        'region': 'us-east-2',
        'database': 'waze',
        'bucket': BUCKET,
        'path': S3_PATH,
        'query': query
    }

session = boto3.Session()
s3 = boto3.resource('s3')

def time_fmt(seconds):
    minutes = int(seconds / 60)
    seconds = seconds % 60
    return "%02d:%02d" % (minutes, seconds)

def athena_query(client, params):
    
    response = client.start_query_execution(
        QueryString=params["query"],
        QueryExecutionContext={
            'Database': params['database']
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
        },
        WorkGroup='EquipeCiro'
    )
    return response

def athena_to_s3(session, params, max_execution = 30):
    max_execution *= 4
    total = max_execution
    client = session.client('athena', region_name=params["region"])
    execution = athena_query(client, params)
    execution_id = execution['QueryExecutionId']
    state = 'RUNNING'

    while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
        print("\r\t",  time_fmt(total*15 - max_execution*15), '/',time_fmt(total*15), end="")
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId = execution_id)

        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                print("")
                return False
            elif state == 'SUCCEEDED':
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                print("")
                return filename
        time.sleep(1*15)
    
    print("")
    return False

def run(query, filename):
    print("Baixando", filename)
    csv_name = athena_to_s3(session, _make_params(query))
    if not csv_name:
        return print("Erro na query", filename)
    s3_path = S3_PATH + '/' + csv_name
    s3.Bucket(BUCKET).download_file(s3_path, filename)
