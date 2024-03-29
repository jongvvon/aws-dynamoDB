import boto3
from botocore.exceptions import ClientError
import json

# DynamoDB 리소스 객체를 생성합니다.
dynamodb = boto3.resource('dynamodb')
# DynamoDB 클라이언트 객체를 생성합니다.
dynamodb_client = boto3.client('dynamodb')

# 테이블을 새로 생성하는 함수입니다.
def create_table(dynamodb):
    table_name = input("테이블 이름을 입력해주세요: ")
    primary_key = input("기본 키 이름을 입력해주세요: ")

    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        print('이미 존재하는 테이블 이름입니다. 다른 이름을 입력해주세요.')
        return
    except ClientError:
        pass

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

    return table, primary_key

# 사용자로부터 테이블 이름을 입력받아 해당 테이블 객체를 반환하는 함수입니다.
def get_table(dynamodb):
    table_name = input("테이블 이름을 입력해주세요: ")
    
    # 해당 테이블의 기본 키 조회
    response = dynamodb_client.describe_table(TableName=table_name)
    primary_key = response['Table']['KeySchema'][0]['AttributeName']
    print(f'해당 테이블의 기본 키는 {primary_key}입니다.')

    try:
        table = dynamodb.Table(table_name)
        table.load()  # 테이블이 존재하는지 확인합니다.
        print(table_name + "에 연결되었습니다.")
    except:
        print('테이블 이름을 확인해주세요')
        return

    return table, primary_key

# 테이블 리스트 조회
def get_table_list():
    print("현재 dynamoDB에 작성되어 있는 Table-List 입니다.")
    response = dynamodb_client.list_tables()
    for table_name in response['TableNames']:
        print(table_name)

# 테이블 전체 조회
def scan_table(table):
    # 테이블 스캔
    response = table.scan()
    # 스캔 결과를 JSON 형식으로 출력
    print(json.dumps(response["Items"], indent=4))

# 사용자로부터 항목의 키를 입력받아 해당 항목을 테이블에서 조회하는 함수입니다.
def get_item(table, key):
    item_key = input("조회할 항목 키 값을 입력해주세요: ")

    try:
        response = table.get_item(
            Key={
                key: item_key
            }
        )
        item = response['Item']
        print("조회된 항목:", json.dumps(item, indent=4))
    except ClientError:
        print('항목 키 값을 확인해주세요')

# 사용자로부터 항목의 키와 새 값을 입력받아 해당 항목을 테이블에서 업데이트하는 함수입니다.
def update_item(table, key):
    item_key = input("접근할 항목 키 값을 입력해주세요: ")
    property_key = input("변경할 속성 키를 입력해주세요: ")
    item_value = input("속성의 새로운 값을 입력해주세요: ")

    table.update_item(
        Key={
            key: item_key
        },
        UpdateExpression=f'SET {property_key} = :val',
        ExpressionAttributeValues={
            ':val': item_value
        }
    )

# 테이블 내부의 아이템을 삭제하는 함수입니다.
def delete_item(table, key):
    item_key = input("삭제할 항목 키 값을 입력해주세요: ")

    table.delete_item(
        Key={
            key: item_key
        }
    )

# 테이블을 삭제하는 함수입니다.
def delete_table(table):
    table.delete()

get_table_list()

while True:
    command = input("""
다음 중 하나의 명령어를 입력해주세요:
g: 테이블 선택
c: 테이블 생성
l: 테이블 리스트 조회
s: 테이블 전체 조회
r: 항목 조회
u: 속성값 변경
di: 아이템 삭제
dt: 테이블 삭제
q: 종료
""")


    if command == 'g':
        table, key = get_table(dynamodb)
    
    elif command == 'l':
        get_table_list()

    elif command == 'c':
        create_table(table)

    elif command == 's':
        if 'table' in locals():
            scan_table(table)
        else:
            print("테이블을 먼저 선택해주세요.")

    elif command == 'r':
        if 'table' in locals():
            get_item(table, key)
        else:
            print("테이블을 먼저 선택해주세요.")

    elif command == 'u':
        if 'table' in locals():
            update_item(table, key)
        else:
            print("테이블을 먼저 선택해주세요.")

    elif command == 'di':
        if 'table' in locals():
            delete_item(table, key)
        else:
            print("테이블을 먼저 선택해주세요.")

    elif command == 'dt':
        if 'table' in locals():
            delete_table(table)
            del table
        else:
            print("테이블을 먼저 선택해주세요.")

    elif command == 'q':
        break

    else:
        print("잘못된 명령어입니다.")
    
