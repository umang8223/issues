import boto3
from datetime import datetime, timedelta

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket name and list of objects
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    expiration_time = datetime.utcnow() - timedelta(days=30)

    # List objects and delete those older than 30 days
    for item in s3.list_objects_v2(Bucket=bucket_name).get('Contents', []):
        if item['LastModified'] < expiration_time:
            s3.delete_object(Bucket=bucket_name, Key=item['Key'])
            print(f"Deleted: {item['Key']}")

    return {'statusCode': 200, 'body': 'Cleanup completed'}
