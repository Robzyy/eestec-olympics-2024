from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import get_settings
import logging
import asyncio

settings = get_settings()
logger = logging.getLogger(__name__)

class AzureLanguageService:
    def __init__(self):
        self.client = TextAnalyticsClient(
            endpoint=settings.AZURE_LANGUAGE_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_LANGUAGE_KEY)
        )

    async def analyze_text(self, text: str):
        try:
            loop = asyncio.get_running_loop()
            
            # Get detailed sentiment analysis
            sentiment = await loop.run_in_executor(
                None, 
                lambda: self.client.analyze_sentiment([text], show_opinion_mining=True)[0]
            )
            
            # Get key phrases
            key_phrases = await loop.run_in_executor(
                None,
                lambda: self.client.extract_key_phrases([text])[0]
            )
            
            # Get language detection
            language = await loop.run_in_executor(
                None,
                lambda: self.client.detect_language([text])[0]
            )

            # Get syntax analysis
            syntax_analysis = await loop.run_in_executor(
                None,
                lambda: self.client.analyze_syntax([text])[0]
            )

            return {
                "grammar_analysis": {
                    "sentence_count": len(syntax_analysis.sentences),
                    "token_count": len(syntax_analysis.tokens),
                    "syntax_tokens": [
                        {
                            "text": token.text,
                            "part_of_speech": token.part_of_speech,
                            "position": token.position
                        } for token in syntax_analysis.tokens
                    ]
                },
                "vocabulary_analysis": {
                    "unique_words": len(set(key_phrases.key_phrases)),
                    "key_phrases": key_phrases.key_phrases
                },
                "style_analysis": {
                    "sentences": [sent.text for sent in syntax_analysis.sentences],
                    "language_score": language.confidence_score
                },
                "language_comments": {
                    "detected_language": language.primary_language.name,
                    "confidence": language.confidence_score
                },
                "sentiment": {
                    "score": {
                        "positive": sentiment.confidence_scores.positive,
                        "neutral": sentiment.confidence_scores.neutral,
                        "negative": sentiment.confidence_scores.negative
                    },
                    "label": sentiment.sentiment,
                    "sentences": [
                        {
                            "text": sent.text,
                            "sentiment": sent.sentiment,
                            "confidence": sent.confidence_scores.__dict__
                        } for sent in sentiment.sentences
                    ]
                },
                "key_phrases": key_phrases.key_phrases,
                "language": language.primary_language.name
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_text: {str(e)}")
            return {
                "error": str(e),
                "grammar_analysis": None,
                "vocabulary_analysis": None,
                "style_analysis": None,
                "language_comments": None,
                "sentiment": None,
                "key_phrases": [],
                "language": None
            }
