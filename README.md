# bangking-system-api

사용 가상환경 miniconda

python 버전정보 3.8

# 패키지 설치 방법

터미널 프로젝트 루트 폴더에서 아래의 명령어를 입력합니다.

```
pip install -r requirements.txt
```

# Project 실행방법

아래의 명령어를 통해 터미널상의 아래의 명령어로 환경변수를 등록하여야 합니다.

```
python manage.py runserver --settings=config.settings.development
```

# Test 방법

Django TestCase를 이용하여 테스트코드를 작성하였습니다.

프로젝트 루트 폴더에서 ㅁㅂ아래의 명령어로 테스트를 진행할 수 있습니다.

```

python manage.py test --settings=config.settings.development

```

```
ex)
request.headers('Authorization' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Mn0.eAHhb0yJoy9456zk5PMafAqGXlpzmsI3ctMkodjDmNQ')
```

# Directory Structure

```
.
├── apps
├── ├── auth (django app dir)
├── ├── transaction (django app dir)
├── └── util
├── config (django project dir)
├── └── settings
├── manage.py
├── Dockerfile
├── requirements.txt
└── .github
```

- apps
  - auth: django로 생성한 기본 앱입니다. 회원가입과 로그인, 토큰발급을 합니다.
  - trnasaction: django로 생성한 기본 앱입니다. 입출금api와 조회 api를 관리합니다.
  - util: 재사용하는 여러가지 모듀들을 관리합니다.
- config: django startproject 명령어로 생성한 기본 프로젝트 폴더 입니다.
- requirements.txt: 설치한 모듈과 버전을 기재한 txt파일 입니다.
- .github: github workflows와 관련한 yml 파일을 관리하는 폴더입니다.
- Dockerfile: docker이미지 빌드에 사용될 파일입니다.

```
./apps/util
├── exceptions.py
├── middlewares.py
├── models.py
├── token.py
├── transforms.py
└── validators.py
```

- exceptions.py: Exception을 상속받아 message, status을 보유한 커스텀 에러 클래스를 관리합니다.
- middlewares.py: 커스텀 미들웨어를 관리합니다.
- models.py: created_at과 updated_at을 관리하는 추상모델 TimeStampModel을 관리합니다.
- token.py: jwt 토큰 검증 데코레이터 validate_token을 관리합니다.
- transforms.py: 시간 변환을 해주는 클래스 TimeTransform과 req.query의 상태검사와 타입변경을 해주는 GetTransactionsQueryTransform을 관리합니다.
- validators.py: 입,출금 api의 request.body의 데이터의 유효성검사를 하는 PostTransactionsJsonValidator를 관리합니다.

```
./config/settings
├── _init__.py
├── base.py
├── development.py
└── production.py
```

개발환경과 배포환경에 따른 settings.py를 선택하여 사용할 수 있도록 분리하였습니다.

base.py를 기본으로 개발환경시 development.py , 배포환경시 production.py를 사용합니다.

# Project Modeling

<img width="897" alt="image" src="https://user-images.githubusercontent.com/100751719/205484815-d67f2446-0003-42a9-a00c-fb23dfd90e02.png">

계좌의 거래 금액과 관련된 amount와 balance는 외화 환율과 이자를 염두해 두어 decimal필드로 설정 하였습니다.

### User 테이블

- Unique = username

- username: 회원의 로그인 id
- password: 로그인 비밀번호 입니다. bcrypt를 이용하여 암호화됩니다.(max_lengt는 bcrypt의 고정길이인 60입니다.)
- credit: 출,입금시 계좌에 이용할 마일리지를 의미합니다. PositiveInt 필드를 이용하여 음수를 허용하지 않습니다.

### Account 테이블

회원의 계좌정보를 관리하는 테이블 입니다.
제약조건: balance는 0 이상이여야 합니다.

- account_number: 암호화되어 관리하는 계좌번호입니다. AES256알고리즘의 고정 반환값인 256을 설정하였습니다.
- balance: 계좌의 잔액입니다.
- password: bcrypt를 이용하여 암호화됩니다.(max_lengt는 bcrypt의 고정길이인 60입니다.)

### AccountType

계좌의 종류를 구별하는 테이블입니다.

ex) 일반예금, 청약저축

### Transaction 테이블

계좌의 거래정보를 관리하는 테이블입니다.

제약조건: balance와 amount 그리고 timestamp는 0 이상이여야 합니다.

인덱스: where문에 사용되는 account, timestamp를 복합인덱스로 사용하였습니다.

- amount: 해당 거래에 거래된 금액입니다
- balance: 해당 거래후의 계좌 잔액입니다.
- is_withdrawal: 해당 거래의 타입이 출금인지 입금인지를 구별하는 컬럼입니다. 1일 경우 출금입니다.
- timestamp: 거래일시를 기록하는 컬럼입니다. index설정을 위하여 datetime이 아닌 float로 설정하였습니다.
- summary: 적요 입니다. 차후 통장거래가 발생할시 통장에 출력을 위해 너무 길지 않게 길이제한을 20으로 두었습니다.

# End-point

### 출,입금 api

body값의 is_withdrawal 값을 이용하여 입,출금을 구분합니다.

**한번의 트랜잭션 처리로 계좌의 잔액과 거래기록의 잔액의 무결성을 보장합니다.**

1. 토큰이 없거나 잘못된 토큰일 시 401에러를 반환 합니다.
2. 토큰에 담긴 id와 계좌의 user_id가 불일치시 403 에러를 반환합니다.
3. 출금 시 거래금액이 user의 credit보다 낮으면 400에러를 반환합니다.
4. path params로 받은 account_id에 해당하는 Account가 없을 시 400에러를 반환합니다.
5. 계좌의 비밀번호가 틀릴 시 401에러를 반환합니다.
6. 계좌의 잔액이 부족할 시 400에러를 반환합니다.

**Request**

```
POST domain/accounts/<int:account_id>/transactions

headers = {Authorizations: access_token} (require)

body = {
        "password"      : str, (require) (계좌비밀번호)
        "amount"        : str, (require) (거래금액)
        "is_withdrawal" : boolean (require) (입,출금 구분)
        "summary"       : str, (optional) (적요)
    }
```

**Response**

```
status = 201

response.json() = {
        'Balance after transaction' : str 소수점4자리 ex)'110000.0000', (거래 후 잔액)
        'Transaction amount'        : int (거래금액)
    }
```

### 거래내역조회 api

거래일시 별 필터링, pagenation, 최신순&오래된순 조회가 가능합니다.

(1900년도 이후의 거래만 조회가능합니다.)

1. 토큰이 없거나 잘못된 토큰일 시 401에러를 반환 합니다.
2. 토큰에 담긴 id와 계좌의 user_id가 불일치시 403 에러를 반환합니다.
3. 1900년도 이후의 거래만 조회가능합니다.

**Request**

```
GET domain/accounts/<int:account_id>/transactions

header = {'Authorizations': access_token} (require)

query_strings = {
        offset           : positive int
        limit            : positive int
        order_by         : recent | ordest
        start_date       : "%Y-%m-d"
        end_date         : "%Y-%m-d"
        transaction_type : deposit | withdrawal | all
    }
```

**Response**

```
status = 200

response.json() = [
        {
            'amount'        : str 소수점4자리 ex)'110000.0000',
            'balance'       : str 소수점4자리 ex)'110000.0000',
            'summary'       : str,
            'timestamp'     : datetime,
            'is_withdrawal' : boolean
        }
    ]

```

### 회원가입 api

**Request**

```
Post domain/auth/users

body = {
    "username" : str,
    "password" : str,
    "first_name" : str,
    "last_name" : str
    }
```

**Response**

```
status = 201

response.json() = [ {'meesage' : 'Success'} ]
```

### 로그인 api

**Request**

```
Post domain/auth/users/signin

body = {
    "username" : str,
    "password" : str,
    }
```

**Response**

```
status = 200

response.json() =  {'access_token' : access_token}
```
