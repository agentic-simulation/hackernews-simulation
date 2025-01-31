from typing import List

from litellm import completion
from pydantic import BaseModel


class ResponseModel(BaseModel):
    thoughts: str
    upvote: bool
    comment: str


class LLM:
    def generate(
        self,
        model: str,
        messages: List[str],
        **kwargs,
    ):
        try:
            res = completion(
                model=model,
                messages=messages,
                response_format=ResponseModel,
                ** kwargs,
            )
            return res
        except Exception as e:
            raise Exception(f"LiteLLM inference failed: {str(e)}")
