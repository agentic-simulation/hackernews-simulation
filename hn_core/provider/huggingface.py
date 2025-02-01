import os
from typing import List, Optional

from huggingface_hub import InferenceClient
from pydantic import BaseModel


class ResponseModel(BaseModel):
    thoughts: str
    upvote: bool
    comment: str

class HuggingFace:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HF_API_KEY")
        self.client = InferenceClient(token=self.api_key)

    def generate(self, model: str, messages: List, response_format: Optional[BaseModel], **kwargs):
        try:
            res = self.client.chat_completion(
                model=model,
                messages=messages,
                response_format={
                    "type": "json",
                    "value": response_format.model_json_schema(),
                },
                **kwargs,
            )
            return res
        except Exception as e:
            raise Exception(f"HuggingFace Endpoint inference failed: {str(e)}")
