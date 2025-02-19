import json
import boto3
from image_processor import process_image

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        image_key = record["s3"]["object"]["key"]

        output_key = process_image(bucket, image_key)
        return {"statusCode": 200, "body": json.dumps(f"Image processed: {output_key}")}
