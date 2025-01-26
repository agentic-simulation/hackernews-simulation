import datetime
from typing import Dict, Optional

from core.constants import AgentAction
from hn_core.model.agent_model import Action


class Post:
    def __init__(
        self,
        title: str,
        url: str,
        text: str,
    ):
        # Static attributes
        self.title = title
        self.url = url
        self.text = text
        self.time_posted = datetime.datetime.now()

        # Initialize interaction stats first
        self.interaction_stats = {
            "post_id": id(self),  # Unique identifier for the post
            "timestamp": self.time_posted,
            "upvotes": 0,
            "downvotes": 0,
            "comments": [],
            "comment_upvotes": {},  # Dictionary mapping comment_id to upvotes
            "comment_downvotes": {},  # Dictionary mapping comment_id to downvotes
            "favorites": 0,
            "interaction_history": [],  # List to store all interactions with timestamps
        }

        # Dynamic attributes that depend on interaction_stats
        self.upvotes = 0
        self.comments = []
        self.rank = (
            self.calculate_rank()
        )  # Now safe to call since interaction_stats exists

    def calculate_rank(self, gravity: float = 1.8) -> float:
        """Calculate post rank using Hacker News ranking algorithm.

        Score = (P-1) / (T+2)^G
        where:
        P = points (upvotes - downvotes)
        T = time since submission (in hours)
        G = Gravity, defaults to 1.8

        Returns:
            float: The calculated rank
        """
        # Calculate points (P) as upvotes minus downvotes
        points = self.interaction_stats["upvotes"] - self.interaction_stats["downvotes"]

        # Calculate time since submission in hours (T)
        time_since_posted = (
            datetime.datetime.now() - self.time_posted
        ).total_seconds() / 3600

        # Apply the formula: (P-1) / (T+2)^G
        # Note: We subtract 1 from points to negate submitter's vote
        rank = (points - 1) / pow((time_since_posted + 2), gravity)

        return rank

    def update(self, action: Action):
        """Update post based on agent actions"""
        if not action:
            return

        # Record the action with timestamp
        timestamp = datetime.datetime.now()
        action_val = action.action.value

        # Update stats based on action type
        if action_val == AgentAction.UPVOTE.value:
            self.interaction_stats["upvotes"] += 1
            self.upvotes += 1  # Update legacy upvotes counter
        elif action_val == AgentAction.DOWNVOTE.value:
            self.interaction_stats["downvotes"] += 1
        elif action_val == AgentAction.FAVORITE.value:
            self.interaction_stats["favorites"] += 1
        elif action_val == AgentAction.CREATE_COMMENT.value:
            comment_id = len(self.interaction_stats["comments"])
            comment = {
                "id": comment_id,
                "text": action.comment_text,
                "timestamp": timestamp,
                "upvotes": 0,
                "downvotes": 0,
            }
            self.interaction_stats["comments"].append(comment)
            self.comments.append(comment)  # Update legacy comments list
        elif action_val == AgentAction.UPVOTE_COMMENT.value:
            comment_id = action.comment_id
            if comment_id is not None:
                self.interaction_stats["comment_upvotes"][comment_id] = (
                    self.interaction_stats["comment_upvotes"].get(comment_id, 0) + 1
                )
        elif action_val == AgentAction.DOWNVOTE_COMMENT.value:
            comment_id = action.comment_id
            if comment_id is not None:
                self.interaction_stats["comment_downvotes"][comment_id] = (
                    self.interaction_stats["comment_downvotes"].get(comment_id, 0) + 1
                )

        # Record interaction in history
        interaction_record = {
            "timestamp": timestamp.isoformat(),
            "action": action_val,
            "agent_id": action.agent_id,
            "comment_id": action.comment_id,
            "comment_text": action.comment_text,
        }
        self.interaction_stats["interaction_history"].append(interaction_record)

        # Recalculate rank after updates
        self.rank = self.calculate_rank()
