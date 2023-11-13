import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize AWS clients
sqs = boto3.client('sqs')
ses = boto3.client('ses')

sender_email = os.environ.get('EMAIL_ID')

def lambda_handler(event, context):
    print(event)
    for record in event['Records']:
        if record.get("body") is None:
            continue

        try:
            json_data = json.loads(record["body"])
            maker_email = json_data["makerEmail"]
            checker_email = json_data["checkerEmail"]
            send_email(maker_email, checker_email, "maker")
            send_email(maker_email, checker_email, "checker")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

def send_email(maker_email, checker_email, to):
    with open("./template.html", "r") as f:
            html_template = f.read()
    subject = "Makerchecker Request made!" if to == "maker" else "New Makerchecker request!"
    
    data = f"Request successfully sent! Email is sent to checker: {checker_email}."\
            if to == "maker" else\
            f"Pending Review! New Makerchecker request from {maker_email}!"
    
    html_template = html_template.replace("INSERT_DATA_HERE", data)
    try:
        response = ses.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [maker_email if to == "maker" else checker_email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': html_template
                    }
                }
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
