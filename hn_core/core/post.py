import json
from datetime import datetime
from typing import Dict

from hn_core.model.model import ClassifyModel
from hn_core.prompts import prompt
from hn_core.provider.litellm import LLM


class Post:
    def __init__(self, title: str, url: str | None = None, text: str | None = None):
        """Initialize a new Post instance representing a Hacker News-style submission.

        This constructor creates a new post with both static and dynamic attributes.
        Posts begin with 1 upvote (from the submitter) and maintain a history of
        state changes for analytics and moderation purposes.

        Args:
            title (str): The headline or title of the post
            url (str): The URL that the post links to (optional, can be empty)
            text (str): The self-post text content (optional, can be empty)
        """
        # Static attributes
        self.title = title
        self.url = url
        self.text = text

        # Dynamic attributes that depend on interaction_stats
        self.upvotes = 1  # Always start with 1 upvote (from submitter)
        self.comments = []
        self.score = 0
        self.penalty = None

        # History to track changes
        self.history = []

    def update_step_state(self, current_time: datetime):
        """Record the current state to history."""
        state = {
            "sim_step": current_time,
            "upvotes": int(self.upvotes),
            "comments_count": int(len(self.comments)),
            "comments": list(self.comments),  # Make a copy to prevent mutation
            "score": float(self.score),  # Ensure score is stored as float
        }
        self.history.append(state)

    def _calculate_penalty(self):
        """calculate post specific penalty"""
        modifier = 1

        # no url penalty
        if not self.url:
            modifier *= 0.4

        # NOTE: definition of lightweight is not clear
        # excluding from penalty until further investigation
        # if not self.text:
        #     modifier *= 0.17

        llm = LLM()
        res = llm.generate(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt.classify.format(title=self.title, text=self.text),
                }
            ],
            response_format=ClassifyModel,
        )

        res_json = json.loads(res.choices[0].message.content)
        categories = res_json["category"]

        if categories["gag"]:
            modifier *= 0.1

        if categories["politics"]:
            modifier *= 0.1

        if categories['dei']
            modifier *= 0.1

        if categories['tutorial']
            modifier *= 0.1

        self.penalty = modifier

    def _calculate_score(self, current_time: int, penalty: float):
        """
        score = ((P-1)**0.8 / (T+2)**1.8) * M

        P = points (upvotes)
        T = time since submission (in hours)
        G = Gravity, defaults to 1.8
        M = Various penalty factor

        """
        # controversial penalty. this needs to be calculated at every timestep because the values change.
        if len(self.comments) > 40 and self.upvotes < len(self.comments):
            penalty *= (self.upvotes / len(self.comments)) ** 3

        points = self.upvotes
        time_since_posted = current_time

        score = ((points - 1) ** 0.8 / ((time_since_posted + 2) ** 1.8)) * penalty

        return score

    def update(self, action: Dict, current_time: datetime):
        """Update post based on agent actions

        Args:
            action (dict): In the format {"upvote": upvote, "comment": comment}
            current_time (int): The current timestep
        """
        # calculate static penalty once in the beginning
        if not self.penalty:
            self._calculate_penalty()

        # Check for upvote action
        if action.get("upvote"):
            self.upvotes += 1

        # Check for comment action
        comment_text = action.get("comment")
        # TODO Comments could eventually have nested comments, so we will need to handle that
        # TODO Comments could also have a score/rank, so we will need to handle that
        if comment_text:
            self.comments.append(comment_text)

        # Update score
        self.score = self._calculate_score(
            current_time=current_time,
            penalty=self.penalty,
        )
