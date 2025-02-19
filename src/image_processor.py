# from PIL import Image
# import io
# import boto3
# import logging
# from src.rekognition_helper import detect_faces

# s3_client = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="us-east-1", aws_access_key_id="test",
#     aws_secret_access_key="test")

# def compress_image(image_data, quality):
#     """Compress image with given quality level"""
#     try:
#         image = Image.open(io.BytesIO(image_data))
#         output_buffer = io.BytesIO()

#         # Preserve format (avoid converting PNG to JPEG)
#         image_format = "JPEG" if image.format != "PNG" else "PNG"
        
#         image.save(output_buffer, format=image_format, quality=quality)
#         return output_buffer.getvalue(), image_format

#     except Exception as e:
#         logging.error(f"Error compressing image: {e}")
#         return None, None

# def process_image(bucket, image_key):
#     """Process the image: Resize, compress, and upload optimized version"""
#     try:
#         # Download original image from S3
#         response = s3_client.get_object(Bucket=bucket, Key=image_key)
#         image_data = response["Body"].read()

#         # Determine compression level
#         has_faces = detect_faces(bucket, image_key)
#         quality = 85 if has_faces else 60

#         # Compress image
#         compressed_image, image_format = compress_image(image_data, quality)
#         if compressed_image is None:
#             return None  # Skip further processing if compression failed

#         # Upload optimized image
#         output_key = f"optimized/{image_key}"
#         s3_client.put_object(Bucket=bucket, Key=output_key, Body=compressed_image, ContentType=f"image/{image_format.lower()}")

#         return output_key

#     except Exception as e:
#         logging.error(f"Error processing image {image_key}: {e}")
#         return None


from PIL import Image
import io
import boto3
import logging
from src.face_det import detect_faces  # Updated import

s3_client = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def compress_image(image_data, quality):
    """Compress image with given quality level."""
    image = Image.open(io.BytesIO(image_data))
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
        quality = 85 if face_count>0 else 60

        # Compress image
        compressed_image = compress_image(image_data, quality)

        # Upload optimized image
        output_key = f"optimized/{image_key}"
        s3_client.put_object(Bucket=bucket, Key=output_key, Body=compressed_image, ContentType="image/jpeg")

        return {"output_key": output_key, "face_count": face_count}
    except Exception as e:
        logging.error(f"Error processing image {image_key}: {e}")
        return None
