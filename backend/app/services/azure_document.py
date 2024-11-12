from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import get_settings
import asyncio

settings = get_settings()

class AzureDocumentService:
    def __init__(self):
        self.client = DocumentAnalysisClient(
            endpoint=settings.AZURE_DOCUMENT_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_DOCUMENT_KEY)
        )

    async def analyze_document(self, document_url: str):
        try:
            # Run the synchronous operations in a thread pool
            loop = asyncio.get_event_loop()
            poller = await loop.run_in_executor(
                None, 
                lambda: self.client.begin_analyze_document_from_url("prebuilt-document", document_url)
            )
            
            # Wait for the result
            result = await loop.run_in_executor(None, poller.result)

            # Extract text and maintain structure
            pages_text = []
            full_text = []

            for page in result.pages:
                page_text = []
                for line in page.lines:
                    page_text.append({
                        "text": line.content,
                        "confidence": line.confidence if hasattr(line, 'confidence') else None,
                        "bounding_box": line.polygon if hasattr(line, 'polygon') else None,
                        "page": page.page_number
                    })
                    full_text.append(line.content)
                pages_text.append(page_text)

            return {
                "status": "success",
                "pages": pages_text,
                "full_text": "\n".join(full_text),
                "page_count": len(result.pages),
                "metadata": {
                    "document_type": result.doc_type if hasattr(result, 'doc_type') else None,
                    "languages": result.languages if hasattr(result, 'languages') else None,
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
