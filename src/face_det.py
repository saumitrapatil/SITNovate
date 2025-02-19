import cv2
import numpy as np
import boto3
import io
import logging

# Load the Haar cascade for face detection. Make sure the XML file is in the same directory.
cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

def detect_faces(bucket, image_key):
    """Detects faces in an image using OpenCV's Haar cascades."""
    try:
        # Create an S3 client (update endpoint_url, region, and credentials as needed)
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",  # For local testing with LocalStack
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test"
        )
        # Download image data from S3
        response = s3_client.get_object(Bucket=bucket, Key=image_key)
        image_data = response["Body"].read()

        # Convert the image data to a NumPy array and decode it
        image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        face_count = len(faces)

        # Log the number of faces detected
        logging.info(f"Detected {face_count} face(s) in image {image_key}.")
        return face_count

    except Exception as e:
        logging.error(f"Error in face detection: {e}")
        return False
