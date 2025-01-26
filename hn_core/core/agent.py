import datetime
import json
import logging
import os
import re
import uuid
from typing import Dict, Optional

from core.constants import ActionMetadata, AgentAction
from core.post import Post
from hn_core.model.agent_model import Action, ActionRecord, Memory
from litellm import completion

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Agent:
    def __init__(
        self,
        model: str,
        bio: str,
        activation_probability: float,
        model_params: Optional[Dict] = None,
    ):
        self.agent_id = str(uuid.uuid1())  # time sortable uuid
        self.bio = bio
        self.model = model
        self.activation_probability = activation_probability
        self.is_active = True
        self.max_retries = 3
        self.model_params = model_params

        # initialize memory
        self.memory = Memory(bio=bio)

        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "agent_prompt.txt"
        )
        with open(prompt_path, "r") as f:
            self.prompt_template = f.read()

    def _add_memory(self, action: Action):
        """Store action in agent's memory with timestamp"""
        timestamp = datetime.datetime.now().isoformat()
        action_record = ActionRecord(
            timestamp=timestamp,
            action=action.action,
            agent_id=action.agent_id,
            comment_id=action.comment_id,
            reasoning=action.reasoning,
        )
        self.memory.actions.append(action_record)

        # increment interaction patterns
        action_type = action.action.value
        self.memory.interaction_patterns[action_type] = (
            self.memory.interaction_patterns.get(action_type, 0) + 1
        )

    def _parse_model_output(self, model_output: str) -> Action:
        # Extract content between ```json and ``` markers
        json_pattern = r"```json\n(.*?)```"
        match = re.search(json_pattern, model_output, re.DOTALL)

        if not match:
            logging.info(
                "Error: Could not find JSON content between ```json and ``` markers"
            )
            return

        json_str = match.group(1).strip()
        try:
            data = json.loads(json_str)
            try:
                # convert string to dataclass
                action = AgentAction(data["action"].strip())
            except (ValueError, AttributeError):
                # default to do nothing if error
                logging.error(f"Invalid action value: {data.get('action')}")
                action = AgentAction.DO_NOTHING

            extracted = Action(
                action=action,
                reasoning=data["reasoning"]
                .replace("<reasoning>", "")
                .replace("</reasoning>", "")
                .strip(),
                agent_id=self.agent_id,
                comment_text=data.get("comment_text"),
                comment_id=data.get("comment_id"),
            )
            return extracted
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {str(e)}")
            return None

    def _get_agent_response(self, post: Post) -> Action:
        """Generate agent response based on persona and post content"""
        # Prepare the action context with emphasis on active engagement
        action_context = "\n".join(
            [
                f"Action: {action.value}\n"
                f"Description: {ActionMetadata.DESCRIPTIONS[action]}\n"
                f"Note: Only choose 'do_nothing' if you genuinely have no interest or expertise in the topic.\n"
                + (
                    "Note: This action requires existing comments on the post.\n"
                    if action
                    in [AgentAction.UPVOTE_COMMENT, AgentAction.DOWNVOTE_COMMENT]
                    else ""
                )
                + (
                    "Note: When choosing this action, you MUST provide a specific comment text.\n"
                    if action == AgentAction.CREATE_COMMENT
                    else ""
                )
                for action in AgentAction
            ]
        )
        post_data = {
            "title": post.title,
            "url": post.url,
            "text": post.text,
            "upvotes": post.upvotes,
            "comment_count": len(post.comments),
            "comments": post.comments,
        }

        # format prompt
        prompt = self.prompt_template.format(
            persona=self.bio,
            interaction_history=json.dumps(self.memory.interaction_patterns, indent=2),
            action_context=action_context,
            post=post_data,
        )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                res = completion(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                if not res or not res.choices:
                    raise ValueError("Empty response from model")

                parsed = self._parse_model_output(res.choices[0].message.content)
                if not parsed:
                    raise ValueError("Failed to parse model output")

                # update memory with new action
                self._add_memory(parsed)
                return parsed

            except Exception as e:
                logging.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                last_error = e

        # do nothing if all retries fail
        logging.error(f"All retry attempts failed. Last error: {str(last_error)}")
        return Action(
            action=AgentAction.DO_NOTHING,
            reasoning=f"Failed to generate output from LLM after {self.max_retries} attempts. Error: {str(last_error)}",
            agent_id=self.agent_id,
            comment_text=None,
            comment_id=None,
        )

    def run(self, post: Post) -> Action:
        """Main execution method for the agent"""
        if not self.is_active:
            return None

        response = self._get_agent_response(post)
        return response
