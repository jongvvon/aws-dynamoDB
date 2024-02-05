# 필요한 라이브러리와 모듈을 임포트합니다
from flask import Flask, request, render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from boto3.dynamodb.conditions import Attr
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from botocore.exceptions import ClientError
import os

# Flask 앱을 생성합니다
app = Flask(__name__)

# DynamoDB 리소스를 생성합니다
dynamodb = boto3.resource('dynamodb')

# DynamoDB의 users 테이블을 선택합니다
table = dynamodb.Table('users')

# Flask-Mail 객체를 생성합니다
mail = Mail(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')  # 이메일 서버 주소
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')  # 이메일 서버의 포트 번호
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')  # TLS 사용 여부
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # 이메일 계정의 사용자 이름
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # 이메일 계정의 비밀번호
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')  # 기본 발신자 이메일 주소

# URLSafeTimedSerializer 객체를 생성합니다. 이 객체는 안전한 URL을 생성하고 확인하는 데 사용됩니다
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# 이메일을 보내는 함수입니다
def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

# 이메일 인증 토큰을 생성하는 함수입니다
def generate_confirmation_token(email):
    return s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# 이메일 인증 토큰을 확인하는 함수입니다
def confirm_token(token, expiration=3600):
    return s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)

# 회원가입을 처리하는 엔드포인트입니다
@app.route('/register', methods=['POST'])
def register():
    # 사용자로부터 입력을 받습니다
    email = request.form.get('email')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    f_code = request.form.get('f_code')

    # 닉네임 중복 확인을 합니다
    response = table.scan(FilterExpression=Attr('nickname').eq(nickname))
    if 'Items' in response and len(response['Items']) > 0:
        return {"message": "Nickname already exists."}, 408

    # 비밀번호를 해시합니다
    hashed_password = generate_password_hash(password)

    try:
        # 사용자 정보를 테이블에 저장합니다
        table.put_item(
            Item={
                'email': email,
                'password': hashed_password,
                'nickname': nickname,
                'f_code': f_code,
                'confirmed': False
            },
            ConditionExpression='attribute_not_exists(email)'
        )
        
        # 이메일 인증 메일을 보냅니다
        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        send_email(email, 'Please confirm your email', html)

        return {"message": "User registered successfully. Please confirm your email."}, 200
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"message": "Email already exists."}, 409
        else:
            return {"message": "An error occurred."}, 500

# 이메일 인증을 처리하는 엔드포인트입니다
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # 토큰을 확인합니다
        email = confirm_token(token)
    except:
        return {"message": "The confirmation link is invalid or has expired."}, 400
    
    # 이메일 인증 상태를 업데이트합니다
    response = table.update_item(
        Key={'email': email},
        UpdateExpression='SET confirmed = :val',
        ExpressionAttributeValues={':val': True}
    )
    
    return {"message": "Email confirmed successfully."}, 200

# 로그인을 처리하는 엔드포인트입니다
@app.route('/login', methods=['POST'])
def login():
    # 사용자로부터 입력을 받습니다
    email = request.form.get('email')
    password = request.form.get('password')

    # 사용자 정보를 조회합니다
    response = table.get_item(Key={'email': email})

    # 사용자 정보가 존재하고 비밀번호가 맞는지 확인합니다
    if 'Item' in response and check_password_hash(response['Item']['password'], password):
        # 이메일 인증 상태를 확인합니다
        if response['Item']['confirmed']:
            return {"message": "Login successful."}, 200
        else:
            return {"message": "Please confirm your email."}, 401
    else:
        return {"message": "Invalid email or password."}, 402

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
