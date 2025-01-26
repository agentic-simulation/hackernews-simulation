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

        # Dynamic attributes that depend on interaction_stats
        self.upvotes = 1
        self.comments = []
        self.score = 0

    def _calculate_score(self, current_time, gravity: float = 1.8) -> float:
        """Calculate post rank using Hacker News ranking algorithm.

        Score = (P-1) / (T+2)^G
        where:
        P = points (upvotes)
        T = time since submission (in hours)
        G = Gravity, defaults to 1.8

        Returns:
            float: The calculated rank
        """
        # TODO: Implement the modifiers
        # TYPE_PENALTY = 0.8 -> Penalty for non-story/poll content
        # NO_URL_PENALTY = 0.4 -> Penalty for posts without a URL
        # SEVERITY_PENALTY = 0.001 -> Penalty for posts with buried content
        # LIGHTWEIGHT_PENALTY = 0.17 -> Penalty for lightweight content
        # GAG_PENALTY = 0.1 -> Penalty for gagged content
        # rank = (base_score / time_decay) * modifiers
        # base_score = (score - 1)^0.8 if (score > 1) else (score - 1)
        # time_decay = time_since_posted + 2 (in hours)

        points = self.upvotes

        # Calculate time since submission in hours (T)
        time_since_posted = current_time  # in hours

        # Apply the formula: (P-1) / (T+2)^G
        # Note: We subtract 1 from points to negate submitter's vote
        score = (points - 1) / pow((time_since_posted + 2), gravity)
        return score

    def update(
        self,
        action: Action,
        current_time,
    ):
        """Update post based on agent actions"""
        if not action:
            return

        timestamp = datetime.datetime.now()
        action_val = action.action.value

        # TODO: agents can take more than one comment
        if action_val == AgentAction.UPVOTE.value:
            self.upvotes += 1  # Update legacy upvotes counter
        elif action_val == AgentAction.CREATE_COMMENT.value:
            # * Comments could eventually have nested comments, so we will need to handle that
            # * Comments could also have a score/rank, so we will need to handle that
            self.comments.append(action.comment_text)

        # TODO: properly implement score calculation
        self.score = self._calculate_score(current_time)
