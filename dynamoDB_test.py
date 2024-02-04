import boto3

# AWS SDK인 boto3를 통해 DynamoDB에 연결
dynamodb = boto3.resource('dynamodb')

# 테이블 생성
table = dynamodb.create_table(
    TableName='TestTable',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'  
        },
        {
            'AttributeName': 'last_name',
            'KeyType': 'RANGE'  
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# 테이블이 생성될 때까지 대기
table.meta.client.get_waiter('table_exists').wait(TableName='TestTable')

# 데이터 입력
table.put_item(
   Item={
        'username': 'testuser',
        'last_name': 'test',
        'age': 30,
        'email': 'testuser@test.com'
    }
)

# 데이터 조회
response = table.get_item(
    Key={
        'username': 'testuser',
        'last_name': 'test'
    }
)
item = response['Item']
print(item)

# 데이터 수정
table.update_item(
    Key={
        'username': 'testuser',
        'last_name': 'test'
    },
    UpdateExpression='SET age = :val1',
    ExpressionAttributeValues={
        ':val1': 31
    }
)

# 데이터 삭제
table.delete_item(
    Key={
        'username': 'testuser',
        'last_name': 'test'
    }
)

# cli 환경 db 조회 시, aws dynamodb scan --table-name TestTable --output json