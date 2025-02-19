import json
import boto3
import logging
from src.image_processor import process_image

s3_client = boto3.client("s3", 
                         endpoint_url="http://localhost:4566", 
                         region_name="us-east-1",
                         aws_access_key_id="test",
                         aws_secret_access_key="test")

def lambda_handler(event, context):
    results = []

    for record in event["Records"]:
        try:
            bucket = record["s3"]["bucket"]["name"]
            image_key = record["s3"]["object"]["key"]
            result = process_image(bucket, image_key)
            if result:
                results.append({
                    "image_key": image_key,
                    "processed": True,
                    "output_key": result["output_key"],
                    "face_count": result["face_count"]
                })
            else:
                results.append({
                    "image_key": image_key,
                    "processed": False,
                    "error": "Processing failed"
                })
            # output_key = process_image(bucket, image_key)

            # if output_key:
            #     results.append({"image_key": image_key, "processed": True, "output_key": output_key})
            # else:
            #     results.append({"image_key": image_key, "processed": False, "error": "Processing failed"})

        except Exception as e:
            logging.error(f"Error processing image event: {e}")
            results.append({"image_key": image_key, "processed": False, "error": str(e)})

    return {"statusCode": 200, "body": json.dumps(results)}
