import json
import uuid
import boto3

ssm_client = boto3.client('ssm')

def get_table_name():
    return ssm_client.get_parameter(Name='cdk_table_name', WithDecryption=True)["Parameter"]["Value"]

dynamodb = boto3.resource('dynamodb')
table_name = get_table_name()
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        
        title = body['title']
        description = body['description']
        status = body['status']

        if not title or not description or not status:
            return generate_response(400, 'Bad request')

        response, task_id = create_item(title, description, status)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            generate_response(201, {"taskId": task_id, "title": title, "description": description, "status": status})

    except Exception as e:
        return generate_response(500, f'Internal Server Error {e}')


def create_item(title, description, status):
    task_id = str(uuid.uuid4())
    response = table.put_item(
        Item={
            'taskId': task_id,
            'title': title,
            'description': description,
            'status': status
        }
    )

    return response, task_id

def generate_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Content-Type': 'application/json',
        },
        'body': json.dumps(body)
    }