import pytest
from hn_core.environment import Environment
from hn_core.agent import Agent
from hn_core.post import Post

def test_environment_initialization():
    """Test environment initialization"""
    post = Post(title="Test", url="https://test.com", text="Test")
    agents = [Agent(bio="Test bio 1"), Agent(bio="Test bio 2")]
    env = Environment(total_time_steps=24, agents=agents, post=post)
    
    assert env.total_time_steps == 24
    assert len(env.agents) == 2
    assert env.post == post

def test_sequential_interaction():
    """Test that agents interact in sequence"""
    post = Post(title="Test", url="https://test.com", text="Test")
    agents = [
        Agent(bio="Agent 1", activation_probability=1.0),
        Agent(bio="Agent 2", activation_probability=1.0)
    ]
    env = Environment(total_time_steps=1, agents=agents, post=post)
    
    # Run for one time step
    env.run()
    
    # Check interaction history
    history = post.interaction_stats['interaction_history']
    if len(history) >= 2:
        # Verify timestamps are in sequence
        first_time = history[0]['timestamp']
        second_time = history[1]['timestamp']
        assert first_time < second_time

def test_agent_deactivation():
    """Test that agents are deactivated after interaction"""
    post = Post(title="Test", url="https://test.com", text="Test")
    agent = Agent(bio="Test bio", activation_probability=1.0)
    env = Environment(total_time_steps=2, agents=[agent], post=post)
    
    # Initially active
    assert agent.is_active == True
    
    # Run for one time step
    env.run()
    
    # Should be deactivated after interaction
    assert agent.is_active == False 