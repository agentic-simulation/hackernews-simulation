import datetime

class Post:
    def __init__(self, title, url, text):
        # Static attributes
        self.title = title
        self.url = url
        self.text = text
        self.time_posted = datetime.datetime.now()

        # Dynamic attributes
        self.upvotes = 0
        self.comments = []
        self.rank = self.calculate_rank()

    def calculate_rank(self, gravity=1.8):
        # TODO: Implement the modifiers
        # TYPE_PENALTY = 0.8 -> Penalty for non-story/poll content
        # NO_URL_PENALTY = 0.4 -> Penalty for posts without a URL
        # SEVERITY_PENALTY = 0.001 -> Penalty for posts with buried content
        # LIGHTWEIGHT_PENALTY = 0.17 -> Penalty for lightweight content
        # GAG_PENALTY = 0.1 -> Penalty for gagged content
        # rank = (base_score / time_decay) * modifiers
        # base_score = (score - 1)^0.8 if (score > 1) else (score - 1)
        # time_decay = time_since_posted + 2 (in hours)

        # TODO: Implement the modifiers
        # For now, we will just use the base score but we will need to implement the modifiers
        
        time_since_posted = (datetime.datetime.now() - self.time_posted).total_seconds() / 3600
        rank = (self.upvotes - 1) / (time_since_posted + 2) ** gravity
        return rank

    def update(self, actions):
        """Update post based on agent actions"""
        if not actions:
            return

        # TODO: actions format could be like defined in agent.py
        # [{'upvote': True, 'comment': "So cool!"}, {'upvote': False, 'comment': None}, ...]

        # TODO: if action is upvote, increment upvotes (i.e. self.upvotes += 1)

        # TODO: if action is comment, append comment to self.comments (i.e. self.comments.append(action['comment'])) 
        # Comments could eventually have nested comments, so we will need to handle that

        # TODO: Recalculate rank after updates (i.e. self.rank = self.calculate_rank())

        raise NotImplementedError("post.update not implemented")
