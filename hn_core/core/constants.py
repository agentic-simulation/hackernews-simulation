from enum import Enum


class AgentAction(Enum):
    DO_NOTHING = "do_nothing"
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    CREATE_COMMENT = "create_comment"
    UPVOTE_COMMENT = "upvote_comment"
    DOWNVOTE_COMMENT = "downvote_comment"
    FAVORITE = "favorite"


class ActionMetadata:
    DESCRIPTIONS = {
        AgentAction.DO_NOTHING: "Return when indifferent about the post's content. Use when the content doesn't align with interests or expertise.",
        AgentAction.UPVOTE: "Return when the post's content is valuable and worth promoting. Use when the content is high-quality and relevant.",
        AgentAction.DOWNVOTE: "Return when the post's content is low-quality or inappropriate. Use when content doesn't meet community standards.",
        AgentAction.CREATE_COMMENT: "Return when having a meaningful contribution or perspective to share. Include comment text.",
        AgentAction.UPVOTE_COMMENT: "Return when a comment provides valuable insight. Include comment_id.",
        AgentAction.DOWNVOTE_COMMENT: "Return when a comment is unhelpful or inappropriate. Include comment_id.",
        AgentAction.FAVORITE: "Return when the content is exceptional and worth saving. Use for highest quality, most relevant content.",
    }
