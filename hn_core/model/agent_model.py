from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from core.constants import ActionMetadata, AgentAction


@dataclass
class Action:
    action: AgentAction
    reasoning: str
    agent_id: str
    comment_text: Optional[str] = None
    comment_id: Optional[str] = None


@dataclass
class ActionRecord:
    timestamp: str
    action: AgentAction
    agent_id: str
    comment_id: Optional[str] = None
    reasoning: Optional[str] = None


@dataclass
class Memory:
    bio: str
    actions: List[ActionRecord] = field(default_factory=list)
    interaction_patterns: Dict[str, int] = field(default_factory=dict)
    posts_seen: Set[str] = field(default_factory=set)
