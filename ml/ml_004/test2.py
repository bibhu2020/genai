import boto3

s3 = boto3.resource(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

for bucket in s3.buckets.all():
    print(bucket.name)
