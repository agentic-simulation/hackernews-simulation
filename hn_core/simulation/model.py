from pydantic import BaseModel


class ResponseModel(BaseModel):
    thoughts: str
    upvote: bool
    comment: str


class ClassifyModel(BaseModel):
    gag: bool
    politics: bool
    dei: bool
    tutorial: bool
