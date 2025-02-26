import json
import time
from typing import Dict, Optional

from hn_core.prompts import prompt
from hn_core.provider.litellm import LLM
from hn_core.utils.logger import get_logger
from litellm import RateLimitError

from .model import ActionModel
from .post import Post

logger = get_logger("hn_agent")


class Agent:
    def __init__(
        self,
        id: str,
        provider: str,
        model: str,
        agent_prompt: str,
        activation_probability: float,
        model_params: Optional[Dict] = None,
    ):
        """Initialize an Agent instance

        Args:
            agent_prompt (str): The persona of the agent
            activation_probability (float): The probability that the agent will be active (0-1)
            model (str): The model to use for generating agent responses
            model_params (Dict): Additional parameters for the model
        """
        self.id = id
        self.agent_prompt = agent_prompt
        self.activation_probability = activation_probability
        self.model = model
        self.model_params = model_params
        self.is_active = True
        self.llm = LLM()

    def _get_agent_response(self, post: Post) -> Dict:
        """Generate agent response based on persona and post content"""

        post_data = {
            "post_title": post.title,
            "post_url": post.url,
            "post_text": post.text,
            "post_upvotes": post.upvotes,
            "post_comments_count": len(post.comments),
            "post_comments": "\n".join(
                f"<comment_{i+1}>{comment}</comment_{i+1}>"
                for i, comment in enumerate(post.comments)
            ),
        }

        last_error = None
        max_retries = 3
        attempt = 0
        ratelimit_attempt = 0
        while attempt < max_retries:
            try:
                res = self.llm.generate(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": self.agent_prompt.format(
                                **post_data,
                            ),
                        }
                    ],
                    response_format=ActionModel,
                    **self.model_params,
                )
                action = json.loads(res.choices[0].message.content)
                return {
                    "upvote": action["upvote"],
                    "comment": action["comment"],
                    "role": action["role"],
                }
            except RateLimitError as e:
                backoff = min(2**ratelimit_attempt + 40, 60)  # Cap at 60 seconds
                logger.warning(
                    f"Rate limit error encountered, retrying after {backoff}s"
                )
                time.sleep(backoff)
                ratelimit_attempt += 1
                continue
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1

        logger.error(
            f"All retry attempts failed. Defaulting to no action. Last error: {str(last_error)}"
        )
        return {
            "upvote": False,
            "comment": None,
            "role": None,
        }

    def run(self, post: Post) -> Dict:
        """Main execution method for the agent"""
        return self._get_agent_response(post)
