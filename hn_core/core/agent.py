import json
import logging
import os
import re
import time
from typing import Dict, Optional

from hn_core.core.constants import ActionFormat
from hn_core.core.post import Post
import litellm
from litellm import completion, RateLimitError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

litellm.suppress_debug_info = True

class Agent:
    def __init__(
        self,
        model: str,
        bio: str,
        activation_probability: float,
        model_params: Optional[Dict] = None,
    ):
        self.bio = bio
        self.model = model
        self.activation_probability = activation_probability
        self.is_active = True
        self.model_params = model_params

        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "agent_prompt.txt"
        )
        with open(prompt_path, "r") as f:
            self.prompt_template = f.read()

    def _parse_model_output(self, model_output: str) -> Dict:
        """Parse the model output into a response format dictionary"""
        try:
            json_pattern = r"```json(.*?)```"
            match = re.search(json_pattern, model_output, re.DOTALL)

            if not match:
                logging.info("Error: Could not find JSON content between ```json and ``` markers")
                raise ValueError("Error: Could not find JSON content between ```json and ``` markers")

            json_str = match.group(1).strip()
            try:
                data = json.loads(json_str)
                if not ActionFormat.validate(data):
                    logging.error(f"Invalid response format: {data}")
                    raise ValueError(f"Invalid response format: {data}")
                return data
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON: {str(e)}")
                raise ValueError(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error parsing model output: {str(e)}")
            raise ValueError(f"Unexpected error parsing model output: {str(e)}")

    def _get_agent_response(self, post: Post) -> Dict:
        """Generate agent response based on persona and post content"""
        # Generate format context dynamically from ActionFormat
        response_format = "```json\n{\n"
        for field, desc in ActionFormat.DESCRIPTIONS.items():
            type_hint = ActionFormat.TYPE_HINTS[field]
            response_format += f'    "{field}": {type_hint}, // {desc}\n'
        response_format = response_format.rstrip(",\n") + "\n}```"

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

        prompt = self.prompt_template.format(
            persona=self.bio,
            response_format=response_format,
            **post_data,
        )

        last_error = None
        max_retries = 5
        attempt = 0
        ratelimit_attempt = 0
        while attempt < max_retries:
            try:
                res = completion(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    **self.model_params,
                )
                action = self._parse_model_output(res.choices[0].message.content)
                return action

            except Exception as e:
                if isinstance(e, RateLimitError):
                    backoff = min(2 ** ratelimit_attempt + 5, 30)  # Cap at 30 seconds
                    logging.warning(f"Rate limit error encountered, retrying after {backoff}s")
                    time.sleep(backoff)
                    ratelimit_attempt += 1
                    continue
                
                logging.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1

        logging.error(f"All retry attempts failed. Last error: {str(last_error)}")
        return ActionFormat.DEFAULT_ACTION

    def run(self, post: Post) -> Dict:
        """Main execution method for the agent"""
        if not self.is_active:
            return ActionFormat.DEFAULT_ACTION

        return self._get_agent_response(post)
