from enum import Enum


class AgentAction(Enum):
    DO_NOTHING = "do_nothing"
    UPVOTE = "upvote"
    CREATE_COMMENT = "create_comment"


class ActionMetadata:
    DESCRIPTIONS = {
        AgentAction.DO_NOTHING: "Return when indifferent about the post's content. Use when the content doesn't align with interests or expertise.",
        AgentAction.UPVOTE: "Return when the post's content is valuable and worth promoting. Use when the content is high-quality and relevant.",
        AgentAction.CREATE_COMMENT: "Return when having a meaningful contribution or perspective to share. Include comment text.",
    }


# class ResponseFormat:
#     # UPVOTE_ACTION -> true | null; desc: lorem ipsum
#     # COMMENT_ACTION -> "lorem" | null; desc:
