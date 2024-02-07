import boto3
from botocore.exceptions import ClientError
import json

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
        print(table_name + "에 연결되었습니다.")
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

    return table, primary_key

# 테이블 전체 조회
def scan_table(table):
    # 테이블 스캔
    response = table.scan()
    # 스캔 결과를 JSON 형식으로 출력
    print(json.dumps(response["Items"], indent=4))


# # 사용자로부터 항목의 키와 값을 입력받아 해당 항목을 테이블에 삽입하는 함수입니다.
# def put_item(table):
#     item_key = input("항목 키 값을 입력해주세요: ")
#     item_value = input("항목 값을 입력해주세요: ")

#     table.put_item(
#         Item={
#             item_key : item_value
#         }
#     )

# 사용자로부터 항목의 키를 입력받아 해당 항목을 테이블에서 조회하는 함수입니다.
def get_item(table, key):
    item_key = input("조회할 항목 키 값을 입력해주세요: ")

    response = table.get_item(
        Key={
            key: item_key
        }
    )
    item = response['Item']
    print("조회된 항목:", json.dumps(item, indent=4))

# # 사용자로부터 항목의 키와 새 값을 입력받아 해당 항목을 테이블에서 업데이트하는 함수입니다.
# def update_item(table, key):
#     item_key = input("업데이트할 항목 키 값을 입력해주세요: ")
#     item_value = input("새로운 항목 값을 입력해주세요: ")

#     table.update_item(
#         Key={
#             key: item_key
#         },
#         #DynamoDB에서는 특정 단어들을 예약어로 간주하며, 이들은 속성 이름으로 사용할 수 없습니다. 오류 메시지에서 볼 수 있듯이, 'value'는 DynamoDB의 예약어 중 하나입니다.
#         #이 문제를 해결하려면 ExpressionAttributeNames 매개변수를 사용하여 속성 이름을 대체해야 합니다. 예를 들어, 'value' 대신 '#v'를 사용하려면 다음과 같이 코드를 수정할 수 있습니다:
#         UpdateExpression='SET #v = :val',
#         ExpressionAttributeNames={
#             '#v': 'value'
#         },
#         ExpressionAttributeValues={
#             ':val': item_value
#         }
#     )

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

while True:
    command = input("명령어를 입력해주세요 (g: 테이블 선택, s: 테이블 전체 조회, r: 항목 조회, di: 아이템 삭제, dt: 테이블 삭제, q: 종료): ")

    if command == 'g':
        table, key = get_or_create_table(dynamodb)
    # elif command == 'p':
    #     if 'table' in locals():
    #         put_item(table)
    #     else:
    #         print("테이블을 먼저 선택해주세요.")
    elif command == 's':
        if 'table' in locals():
            scan_table(table)
        else:
            print("테이블을 먼저 선택해주세요.")
    elif command == 'r':
        if 'table' in locals():
            get_item(table, key)
            print(table)
        else:
            print("테이블을 먼저 선택해주세요.")
    # elif command == 'u':
    #     if 'table' in locals():
    #         update_item(table, key)
    #     else:
    #         print("테이블을 먼저 선택해주세요.")
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
