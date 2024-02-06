import boto3
from botocore.exceptions import ClientError

# DynamoDB 리소스 객체를 생성합니다.
dynamodb = boto3.resource('dynamodb')

# 사용자로부터 테이블 이름을 입력받아 해당 테이블 객체를 반환하는 함수입니다.
# 해당 테이블이 존재하지 않으면 새로 생성합니다.
def get_or_create_table(dynamodb):
    table_name = input("테이블 이름을 입력해주세요: ")
    primary_key = input("기본 키 이름을 입력해주세요: ")

    try:
        table = dynamodb.Table(table_name)
        table.load()  # 테이블이 존재하는지 확인합니다.
    except ClientError as e:
        # ResourceNotFoundException이 발생하면 테이블을 새로 생성합니다.
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': primary_key,
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': primary_key,
                        'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

    return table

# 사용자로부터 항목의 키와 값을 입력받아 해당 항목을 테이블에 삽입하는 함수입니다.
def put_item(table):
    item_key = input("항목 키 값을 입력해주세요: ")
    item_value = input("항목 값을 입력해주세요: ")

    table.put_item(
        Item={
            'id': item_key,
            'value': item_value
        }
    )

# 사용자로부터 항목의 키를 입력받아 해당 항목을 테이블에서 조회하는 함수입니다.
def get_item(table):
    item_key = input("조회할 항목 키 값을 입력해주세요: ")

    response = table.get_item(
        Key={
            'id': item_key
        }
    )
    item = response['Item']
    print("조회된 항목:", item)

# 사용자로부터 항목의 키와 새 값을 입력받아 해당 항목을 테이블에서 업데이트하는 함수입니다.
def update_item(table):
    item_key = input("업데이트할 항목 키 값을 입력해주세요: ")
    item_value = input("새로운 항목 값을 입력해주세요: ")

    table.update_item(
        Key={
            'id': item_key
        },
        UpdateExpression='SET value = :val',
        ExpressionAttributeValues={
            ':val': item_value
        }
    )

# 테이블을 삭제하는 함수입니다.
def delete_table(table):
    table.delete()

while True:
    command = input("명령어를 입력해주세요 (g: 테이블 선택, p: 항목 삽입, r: 항목 조회, u: 항목 업데이트, d: 테이블 삭제, q: 종료): ")

    if command == 'g':
        table = get_table(dynamodb)
    elif command == 'p':
        if 'table' in locals():
            put_item(table)
        else:
            print("테이블을 먼저 선택해주세요.")
    elif command == 'r':
        if 'table' in locals():
            get_item(table)
        else:
            print("테이블을 먼저 선택해주세요.")
    elif command == 'u':
        if 'table' in locals():
            update_item(table)
        else:
            print("테이블을 먼저 선택해주세요.")
    elif command == 'd':
        if 'table' in locals():
            delete_table(table)
            del table
        else:
            print("테이블을 먼저 선택해주세요.")
    elif command == 'q':
        break
    else:
        print("잘못된 명령어입니다.")
