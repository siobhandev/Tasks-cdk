import json
import boto3

ssm_client = boto3.client('ssm')

def get_table_name():
    return ssm_client.get_parameter(Name='cdk_table_name', WithDecryption=True)["Parameter"]["Value"]

dynamodb = boto3.resource('dynamodb')
table_name = get_table_name()
table = dynamodb.Table(table_name)

def handler(event, context):
    print("Event", event)
    try:
        if event['httpMethod'] != 'PUT':
            return generate_response(405, f'Method {event["httpMethod"]} not allowed')
        
        task_id = event["pathParameters"]["taskId"]
        body = json.loads(event['body'])
        response = update_item(task_id, body)
        if response['Attributes']:
            return generate_response(200, response['Attributes'])
    except Exception as e:
            print("Error", e)
            return generate_response(500, f'Internal server error {e}')

def update_item(task_id, body):
    response = table.update_item(
        key ={
            "taskId": task_id
        },
        UpdateExpression="SET title = :title, description = :description, #st = :status",
        ExpressionAttributeValues={
            ":title": body['title'],
            ":description": body['description'],
            ":status": status
        },
        ExpressionAttributeName={
            "#st": "status"
        },
        ReturnValues="ALL_NEW"
    )
    return response

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