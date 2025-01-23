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
        if event['httpMethod'] != 'GET':
            return generate_response(405, f'Method {event["httpMethod"]} not allowed')
        
        task_id = event["pathParameters"]["taskId"]

        item = get_item(task_id)
        return generate_response(200, item)
    except Exception as e:
            print("Error", e)
            return generate_response(500, f'Internal server error {e}')


def get_item(pk):
    response = table.get_item(
        Key={
            'taskId': pk,
        }
    )
    return response.get('Item', {})


def generate_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Content-Type': 'application/json',
        },
        'body': json.dumps(body)
    }