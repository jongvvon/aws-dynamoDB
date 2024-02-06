import boto3

def delete_table():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('users')
    table.delete()


delete_table()
