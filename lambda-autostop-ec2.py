import os
import json
import boto3
import urllib.request
from datetime import datetime, timezone, timedelta
JST = timezone(timedelta(hours=+9), 'JST')

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
LINE_TOKEN = os.environ['LINE_TOKEN']


def lambda_handler(event, context):

    ec2 = boto3.client('ec2')

    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            },
        ],
    )

    
    instance_ids = []
    messages = []
    
    for reservations in response["Reservations"]:
        for instance in reservations["Instances"]:
            
            instance_id = instance["InstanceId"]
            launch_time = instance["LaunchTime"] + timedelta(hours=+9)
            instance_state = instance["State"]["Name"]
            instance_type = instance["InstanceType"]
            tags = instance["Tags"]
            
            # Get Instance name
            instance_name = ""
            for tag in tags:
                if tag["Key"].lower() == "Name":
                    instance_name = tag["Value"].lower()
            
            # Get Stop State
            for tag in tags:
                if tag["Key"].lower() == "auto_stop" and tag["Value"].lower()=="false":
                    pass
                else:
                    # STOP!! INSTANCE
                    instance_ids.append(instance_id)
                    message = f"[{instance_name}] {instance_type}-{launch_time}"
                    messages.append(message)

    response = ec2.stop_instances(
        InstanceIds=instance_ids, 
    )

    
    title = "EC2 KILLAR (Acount:FiFi)"
    detail = "\n".join(messages)

    post_slack(title, detail)
    post_line(title, detail)
    
    return {
        'statusCode': 200,
        'body': response #json.dumps('Hello from Lambda!')
    }


def post_slack(title, detail):
    print(SLACK_WEBHOOK_URL)
    url = SLACK_WEBHOOK_URL
    set_fileds = [{"title":title, "value":detail, "short":False}]
    data = {"attachments":[{'color':'danger', 'fields':set_fileds}]}
    request_headers = {'Content-Type': 'application/json; charset=utf-8'}
    body = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        url=url, data=body, method='POST', headers=request_headers)
    urllib.request.urlopen(request)
    pass


def post_line(title, detail):
    
    message = title + "\n\n" + detail
    
    payload = {'message': message}

    payload = urllib.parse.urlencode(payload).encode("utf-8")
    
    request_headers = {'Authorization': 'Bearer ' + LINE_TOKEN}
    
    
    request = urllib.request.Request(
        url='https://notify-api.line.me/api/notify', 
        data=payload,
        method='POST',
        headers=request_headers)
        
    urllib.request.urlopen(request)
    
    
