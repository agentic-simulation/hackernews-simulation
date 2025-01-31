class ActionFormat:
    """Defines the expected format and schema for agent responses"""

    # Action responses
    UPVOTE = "upvote"  # Type: bool | None
    COMMENT = "comment"  # Type: str | None
    # VIEW_URL = "view_url"  # Type: bool | None

    # Documentation for each field
    DESCRIPTIONS = {
        UPVOTE: "Indicating whether to upvote the post. `true` to upvote, `null` to take no action.",
        COMMENT: "String containing comment text to post. `null` if no comment should be made.",
    }

    # Type hints for each field
    TYPE_HINTS = {
        UPVOTE: "<bool|null>",
        COMMENT: "<string|null>",
    }

    # Default action when parsing/processing fails
    DEFAULT_ACTION = {
        UPVOTE: None,
        COMMENT: None,
    }

    @classmethod
    def validate(cls, response: dict) -> bool:
        """Validates that a response matches the expected format"""
        valid_keys = {cls.UPVOTE, cls.COMMENT}
        return (
            isinstance(response, dict)
            and set(response.keys()).issubset(valid_keys)
            and (response.get(cls.UPVOTE) is None or isinstance(response.get(cls.UPVOTE), bool))
            and (response.get(cls.COMMENT) is None or isinstance(response.get(cls.COMMENT), str))
        )
