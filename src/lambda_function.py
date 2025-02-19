import json
from PIL import Image
import cv2
import numpy as np
import io
import boto3
import logging

s3_client = boto3.client("s3")

# Load the Haar cascade for face detection. Make sure the XML file is in the same directory.
cascade_path = "./haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)


def detect_faces(bucket, image_key):
    """Detects faces in an image using OpenCV's Haar cascades."""
    try:
        # Create an S3 client (update endpoint_url, region, and credentials as needed)
        s3_client = boto3.client("s3")
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

def compress_image(image_data, quality):
    """Compress image with given quality level."""
    image = Image.open(io.BytesIO(image_data))
    if image.mode == "RGBA":
        image = image.convert("RGB")

    output_buffer = io.BytesIO()
    # Save as JPEG (adjust if needed for other formats)
    image.save(output_buffer, format="JPEG", quality=quality)
    return output_buffer.getvalue()


def process_image(bucket, image_key):
    """Process the image: Resize, compress, and upload optimized version."""
    try:
        # Download original image from S3
        response = s3_client.get_object(Bucket=bucket, Key=image_key)
        image_data = response["Body"].read()

        # Use the face detector to determine compression quality
        face_count = detect_faces(bucket, image_key)
        quality = 85 if face_count > 0 else 60

        # Compress image
        compressed_image = compress_image(image_data, quality)

        # Upload optimized image
        output_key = f"optimized/{image_key}"
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=compressed_image,
            ContentType="image/jpeg",
        )

        return {"output_key": output_key, "face_count": face_count}
    except Exception as e:
        logging.error(f"Error processing image {image_key}: {e}")
        return None


def lambda_handler(event, context):
    results = []

    for record in event["Records"]:
        try:
            bucket = record["s3"]["bucket"]["name"]
            image_key = record["s3"]["object"]["key"]
            result = process_image(bucket, image_key)
            if result:
                results.append(
                    {
                        "image_key": image_key,
                        "processed": True,
                        "output_key": result["output_key"],
                        "face_count": result["face_count"],
                    }
                )
            else:
                results.append(
                    {
                        "image_key": image_key,
                        "processed": False,
                        "error": "Processing failed",
                    }
                )
        except Exception as e:
            logging.error(f"Error processing image event: {e}")
            results.append(
                {"image_key": image_key, "processed": False, "error": str(e)}
            )

    return {"statusCode": 200, "body": json.dumps(results)}
