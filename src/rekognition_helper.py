import boto3
import logging

rekognition_client = boto3.client("rekognition", endpoint_url="http://localhost:4566", region_name="us-east-1", aws_access_key_id="test",
    aws_secret_access_key="test")

def detect_faces(bucket, image_key):
    """Uses Amazon Rekognition to detect faces in an image"""
    try:
        response = rekognition_client.detect_faces(
            Image={'S3Object': {'Bucket': bucket, 'Name': image_key}},
            Attributes=['ALL']
        )
        return len(response['FaceDetails']) > 0  # Returns True if faces are detected

    except Exception as e:
        logging.error(f"Error in face detection: {e}")
        return False  # Assume no faces if an error occurs
