from typing import List, Optional

from pydantic import BaseModel

from litellm import completion


class LLM:
    def generate(
        self,
        model: str,
        messages: List[str],
        response_format: Optional[BaseModel] = None,
        **kwargs,
    ):
        try:
            res = completion(
                model=model,
                messages=messages,
                response_format=response_format,
                **kwargs,
            )
            return res
        except Exception as e:
            raise Exception(f"LiteLLM inference failed: {str(e)}")
