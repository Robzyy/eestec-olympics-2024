from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from app.core.config import get_settings
import time
import asyncio

settings = get_settings()

class AzureVisionService:
    def __init__(self):
        self.client = ComputerVisionClient(
            endpoint=settings.AZURE_VISION_ENDPOINT,
            credentials=CognitiveServicesCredentials(settings.AZURE_VISION_KEY)
        )

    async def extract_text(self, image_data):
        try:
            loop = asyncio.get_event_loop()
            
            read_response = await loop.run_in_executor(
                None,
                lambda: self.client.read_in_stream(image_data, raw=True)
            )
            
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            while True:
                read_result = await loop.run_in_executor(
                    None,
                    lambda: self.client.get_read_result(operation_id)
                )
                if read_result.status not in ['notStarted', 'running']:
                    break
                await asyncio.sleep(1)

            if read_result.status == OperationStatusCodes.succeeded:
                text_lines = []
                full_text = []
                page_results = []

                for page_num, text_result in enumerate(read_result.analyze_result.read_results):
                    page_lines = []
                    for line in text_result.lines:
                        confidence = None
                        if hasattr(line, 'appearance'):
                            confidence = getattr(line.appearance, 'confidence', None)
                        elif hasattr(line, 'confidence'):
                            confidence = line.confidence

                        line_data = {
                            "text": line.text,
                            "confidence": confidence,
                            "bounding_box": line.bounding_box if hasattr(line, 'bounding_box') else None,
                            "language": line.language if hasattr(line, 'language') else None,
                            "page": page_num + 1
                        }
                        text_lines.append(line_data)
                        page_lines.append(line_data)
                        full_text.append(line.text)
                    
                    page_results.append({
                        "page_number": page_num + 1,
                        "lines": page_lines,
                        "page_text": "\n".join(line["text"] for line in page_lines)
                    })

                confidence_values = [line["confidence"] for line in text_lines if line["confidence"] is not None]
                average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else None

                return {
                    "status": "success",
                    "text_lines": text_lines,
                    "full_text": "\n".join(full_text),
                    "page_count": len(page_results),
                    "pages": page_results,
                    "metadata": {
                        "total_lines": len(text_lines),
                        "total_pages": len(page_results),
                        "average_confidence": average_confidence
                    }
                }
            
            return {
                "status": "error",
                "text_lines": [],
                "full_text": "",
                "error": "Failed to extract text",
                "page_count": 0,
                "pages": [],
                "metadata": None
            }

        except Exception as e:
            return {
                "status": "error",
                "text_lines": [],
                "full_text": "",
                "error": str(e),
                "page_count": 0,
                "pages": [],
                "metadata": None
            }