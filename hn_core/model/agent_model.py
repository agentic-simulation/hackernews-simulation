from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from core.constants import ActionMetadata, AgentAction


@dataclass
class Action:
    action: AgentAction
    reasoning: str
    comment_text: Optional[str] = None


@dataclass
class ActionRecord:
    action: AgentAction
    reasoning: Optional[str] = None


@dataclass
class Memory:
    bio: str
    actions: List[ActionRecord] = field(default_factory=list)
