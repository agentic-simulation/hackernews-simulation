from typing import Literal

from pydantic import BaseModel


class ActionModel(BaseModel):
    thoughts: str
    upvote: bool
    comment: str
    role: Literal[
        "Software Engineer",
        "Research Scientist",
        "Business Analyst",
        "Product Designer",
        "Technology Analyst",
    ]


class ClassifyModel(BaseModel):
    gag: bool
    politics: bool
    dei: bool
    tutorial: bool
