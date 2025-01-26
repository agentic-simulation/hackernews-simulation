import pytest
from hn_core.post import Post
from hn_core.agent import AgentAction

def test_post_initialization():
    """Test post initialization"""
    post = Post(
        title="Test Post",
        url="https://test.com",
        text="Test content"
    )
    assert post.title == "Test Post"
    assert post.upvotes == 0
    assert isinstance(post.interaction_stats, dict)

def test_post_update_upvote():
    """Test post update with upvote action"""
    post = Post(title="Test", url="https://test.com", text="Test")
    initial_upvotes = post.upvotes
    
    action = {
        'action': AgentAction.UPVOTE.value,
        'agent': None
    }
    
    post.update(action)
    assert post.upvotes == initial_upvotes + 1
    assert post.interaction_stats['upvotes'] == 1

def test_post_update_comment():
    """Test post update with comment action"""
    post = Post(title="Test", url="https://test.com", text="Test")
    initial_comments = len(post.comments)
    
    action = {
        'action': AgentAction.CREATE_COMMENT.value,
        'comment_text': "Test comment",
        'agent': None
    }
    
    post.update(action)
    assert len(post.comments) == initial_comments + 1
    assert post.comments[-1]['text'] == "Test comment"

def test_rank_calculation():
    """Test post rank calculation"""
    post = Post(title="Test", url="https://test.com", text="Test")
    initial_rank = post.rank
    
    # Add an upvote
    action = {
        'action': AgentAction.UPVOTE.value,
        'agent': None
    }
    post.update(action)
    
    # Rank should change after upvote
    assert post.rank != initial_rank 