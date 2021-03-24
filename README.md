# Provision EC2 Instance using Flask and Boto3

Steps to run:

- Create virtual environment: `python3 -m virtualenv --python=python3 .env`
- Activate virtual environment: `source .env/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Configure aws, using `aws configure`
- If custom aws configuration file is created, `export AWS_CONFIG_FILE=/path/to/aws/config/ini/file`
- Run server: `FLASK_APP=app.py flask run`

Prerequisites before trying to create new instance:

- Create key pair and store private file if you want to SSH.
- Create Security Group for the instance to allow inbound calls.

Assumptions:

- All prerequisites have been satisfied. Functions to do that are: `create_key_pair` & `create_security_group`.

Sample AWS Config INI file:
```
[default]
aws_secret_access_key =  <your_aws_account_access_key> 
aws_access_key_id = <your_aws_account_access_key_id>
region = <aws_region_like_ap-south-1>

```

Sample Curl Request:

Create:

```
curl -X POST http://localhost:5000/create -H 'Content-Type: application/json' -d '{"instance_type": "t2.micro"}'
```

Status:

```
curl -X GET http://localhost:5000/status\?instance_id\=INSTANCE_ID
```

Note:

- Key pair creation can be optional, if access of instance is not required by end user.
