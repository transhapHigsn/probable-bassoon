# Provision EC2 Instance using Flask and Boto3

Steps to run:

- `export AWS_CONFIG_FILE=/path/to/aws/config/ini/file`
- `FLASK_APP=app.py flask run`

Prerequisites before trying to create new instance:

- Create key pair and store private file if you want to SSH.
- Create Security Group for the instance to allow inbound calls.

Sample Curl Request:

Create:

```
curl -X POST http://localhost:5000/create -H 'Content-Type: application/json' -d '{"instance_type": "t2.micro"}'
```

Status:

```
curl -X GET http://localhost:5000/status\?instance_id\=INSTANCE_ID
```
