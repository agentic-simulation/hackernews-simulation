import pytest
from hn_core.agent import Agent, AgentAction
from hn_core.post import Post

def test_agent_initialization():
    """Test agent initialization with default values"""
    agent = Agent(bio="Test bio")
    assert agent.bio == "Test bio"
    assert agent.is_active == True
    assert isinstance(agent.memory, dict)

def test_agent_response():
    """Test agent response generation"""
    agent = Agent(bio="I am a tech enthusiast")
    post = Post(
        title="New Programming Language Released",
        url="https://example.com",
        text="A new programming language focused on AI development"
    )
    
    response = agent.get_agent_response(post)
    assert isinstance(response, dict)
    assert 'action' in response
    assert response['action'] in [action.value for action in AgentAction]

def test_memory_update():
    """Test agent memory updates after actions"""
    agent = Agent(bio="Test bio")
    initial_memory_length = len(agent.memory['actions'])
    
    action = {
        'action': AgentAction.UPVOTE.value,
        'post_id': 123,
        'reasoning': "Good content"
    }
    
    agent.add_memory(action)
    assert len(agent.memory['actions']) == initial_memory_length + 1
    assert agent.memory['interaction_patterns'].get(AgentAction.UPVOTE.value) == 1 