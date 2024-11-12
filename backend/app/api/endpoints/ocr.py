from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.models.user import User


load_dotenv()
router = APIRouter(dependencies=[Depends(get_current_user)])


# Set up your Computer Vision client
endpoint = os.getenv("AZURE_VISION_ENDPOINT")
subscription_key = os.getenv("AZURE_VISION_KEY")
client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Choose an image path
image_path = "image.png"

# Open the image and extract text
with open(image_path, "rb") as image_stream:
    response = client.read_in_stream(image_stream, raw=True)

# Get operation ID and wait for the result
operation_location = response.headers["Operation-Location"]
operation_id = operation_location.split("/")[-1]
while True:
    result = client.get_read_result(operation_id)
    if result.status not in [OperationStatusCodes.running]:
        break
    time.sleep(1)

# Display extracted text
if result.status == OperationStatusCodes.succeeded:
    for line in result.analyze_result.read_results[0].lines:
        print(line.text)
