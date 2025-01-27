from hn_core.core.constants import ActionFormat


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

        # Dynamic attributes that depend on interaction_stats
        self.upvotes = 1 # Always start with 1 upvote
        self.comments = []
        self.score = 0

        # History to track changes
        self.history = []
        self._record_history()

    def _record_history(self):
        """Record the current state to history."""
        state = {
            'upvotes': self.upvotes,
            'comments': list(self.comments),  # Make a copy to prevent mutation
            'score': self.score
        }
        self.history.append(state)

    def _calculate_score(self, current_time, gravity: float = 1.8) -> float:
        """Calculate post rank using Hacker News ranking algorithm.

        Score = (P-1) / (T+2)^G * modifiers
        where:
        P = points (upvotes)
        T = time since submission (in hours)
        G = Gravity, defaults to 1.8

        Modifiers:
            TYPE_PENALTY = 0.8 -> Penalty for non-story/poll content
            NO_URL_PENALTY = 0.4 -> Penalty for posts without a URL
            SEVERITY_PENALTY = 0.001 -> Penalty for posts with buried content
            LIGHTWEIGHT_PENALTY = 0.17 -> Penalty for lightweight content
            GAG_PENALTY = 0.1 -> Penalty for gagged content

        Returns:
            float: The calculated rank
        """
        # TODO: Implement the modifiers
        # TYPE_PENALTY = 0.8 -> Penalty for non-story/poll content
        # SEVERITY_PENALTY = 0.001 -> Penalty for posts with buried content
        # LIGHTWEIGHT_PENALTY = 0.17 -> Penalty for lightweight content
        # GAG_PENALTY = 0.1 -> Penalty for gagged content
        # rank = (base_score / time_decay) * modifiers
        # base_score = (score - 1)^0.8 if (score > 1) else (score - 1)
        # time_decay = time_since_posted + 2 (in hours)

        modifiers = 1
        
        # NO_URL_PENALTY
        if not self.url:
            modifiers *= 0.4

        points = self.upvotes

        # Calculate time since submission in hours (T)
        time_since_posted = current_time  # in hours

        # Apply the formula: (P-1) / (T+2)^G * modifiers
        # Note: We subtract 1 from points to negate submitter's vote
        score = (points - 1) / pow((time_since_posted + 2), gravity) * modifiers
        return score

    def update(
        self,
        action: ActionFormat,
        current_time,
    ):
        """Update post based on agent actions"""

        # Check for upvote action
        if action.get(ActionFormat.UPVOTE):
            self.upvotes += 1

        # Check for comment action
        comment_text = action.get(ActionFormat.COMMENT)
        # * Comments could eventually have nested comments, so we will need to handle that
        # * Comments could also have a score/rank, so we will need to handle that
        if comment_text:
            self.comments.append(comment_text)

        # Update score
        self.score = self._calculate_score(current_time)

        # Record the new state in history
        self._record_history()
