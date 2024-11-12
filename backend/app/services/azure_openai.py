from openai import AsyncAzureOpenAI
from app.core.config import get_settings
from typing import Optional, Dict, Any
import json

settings = get_settings()

class AzureOpenAIService:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-15-preview"
        )

    async def get_completion(self, prompt: str, max_tokens: int = 4000) -> str:
        try:
            system_prompt = """You are an expert grading assistant. 
            Return response in this exact JSON format:
            {
                "status": "success",
                "error": null,
                "overall_score": float,
                "grading_results": [
                    {
                        "criterion": string,
                        "score": float,
                        "feedback": string
                    }
                ],
                "detailed_feedback": string,
                "improvement_suggestions": [string],
                "language_quality": {
                    "grammar": string,
                    "vocabulary": string,
                    "style": string,
                    "comments": string
                },
                "strengths": [string],
                "weaknesses": [string]
            }"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "overall_score": 0,
                "grading_results": [],
                "detailed_feedback": "",
                "improvement_suggestions": [],
                "language_quality": {
                    "grammar": "Error occurred",
                    "vocabulary": "Error occurred",
                    "style": "Error occurred",
                    "comments": str(e)
                },
                "strengths": [],
                "weaknesses": []
            })

    async def analyze_text(self, text: str, max_tokens: int = 4000):
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert grading assistant. Provide detailed analysis and feedback in JSON format."},
                    {"role": "user", "content": text}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "overall_score": 0,
                "grading_results": [],
                "detailed_feedback": "",
                "improvement_suggestions": [],
                "language_quality": {
                    "grammar": "Error occurred",
                    "vocabulary": "Error occurred",
                    "style": "Error occurred",
                    "comments": str(e)
                },
                "strengths": [],
                "weaknesses": []
            })

    async def review_code(
        self, 
        code: str, 
        language: str,
        assignment_prompt: Optional[str] = None,
        requirements: Optional[list] = None,
        max_tokens: int = 4000
    ) -> str:
        try:
            system_prompt = """You are an expert code reviewer. Analyze the code and provide a detailed review in the following JSON format:
            {
                "Overall Code Quality": number (0-100),
                "Security Analysis": "string with security assessment",
                "Performance Analysis": "string with performance assessment",
                "Best Practices": {
                    "category1": "description1",
                    "category2": "description2"
                },
                "Specific Issues Found": [
                    "issue1",
                    "issue2"
                ],
                "Improvement Suggestions with Code Examples": {
                    "suggestion1": "details1",
                    "suggestion2": "details2"
                }
            }"""

            user_prompt = f"""Review this {language} code:

            ```
            {code}
            ```

            Assignment Prompt: {assignment_prompt if assignment_prompt else 'Not provided'}
            Requirements: {requirements if requirements else 'Not provided'}"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            return response.choices[0].message.content

        except Exception as e:
            return json.dumps({
                "Overall Code Quality": 0,
                "Security Analysis": f"Error: {str(e)}",
                "Performance Analysis": "",
                "Best Practices": {},
                "Specific Issues Found": [],
                "Improvement Suggestions with Code Examples": {}
            })

    async def classify_code(
        self,
        code: str,
        include_features: bool = True,
        include_frameworks: bool = True,
        max_tokens: int = 2000
    ) -> str:
        try:
            system_prompt = """You are an expert in programming languages and code analysis.
            Your task is to identify programming languages and analyze code features with high accuracy.
            
            Return the response in this exact JSON format:
            {
                "primary_language": "string",
                "confidence_score": float,
                "possible_languages": [
                    {
                        "language": "string",
                        "score": float
                    }
                ],
                "features": {
                    "syntax_elements": ["string"],
                    "programming_paradigms": ["string"],
                    "language_version_hints": ["string"],
                    "frameworks_and_libraries": ["string"],
                    "special_language_features": ["string"]
                }
            }
            
            Make sure each possible language has both a language name (string) and a score (float between 0 and 1)."""

            user_prompt = f"""Analyze this code snippet:

            ```
            {code}
            ```

            Identify:
            1. Primary programming language
            2. Confidence score (0-1) for the identification
            3. Other possible languages with their confidence scores

            {'''Also analyze:
            - Syntax elements used
            - Programming paradigms present
            - Language version hints
            - Frameworks and libraries used
            - Special language features''' if include_features else ''}"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            # Return the raw response content
            return response.choices[0].message.content

        except Exception as e:
            return json.dumps({
                "primary_language": "unknown",
                "confidence_score": 0.0,
                "possible_languages": [],
                "features": None,
                "error": str(e)
            })
