import litellm
from enum import Enum
from typing import Optional, Dict, List
import json
import datetime
import os

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

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
        AgentAction.FAVORITE: "Return when the content is exceptional and worth saving. Use for highest quality, most relevant content."
    }

class Agent:
    def __init__(self, 
                 model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 
                 temperature: float = 0.9,
                 bio: str = "", 
                 activation_probability: float = 0.5,
                 is_test: bool = False):
        
        self.bio = bio
        self.model = model
        self.temperature = temperature
        self.activation_probability = activation_probability
        self.is_active = True
        self.is_test = is_test
        self.max_retries = 3
        
        # Enhanced memory structure
        self.memory = {
            'bio': bio,
            'actions': [],  # List of past actions with timestamps
            'interaction_patterns': {},  # Will store action frequencies
            'posts_seen': set()  # Track unique posts interacted with
        }

        # Load agent prompt template
        # if is_test:
        #     template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
        #                                'tests', 'mock_prompt_template.txt')
        # else:
        template_path = os.path.join(os.path.dirname(__file__), 
                                    'prompts', 'agent_prompt_template.txt')
        
        try:
            with open(template_path, "r") as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            # Fallback to a basic template if file not found
            self.prompt_template = """
            Persona: {persona}
            History: {interaction_history}
            Actions: {action_context}
            Post: {post.title}
            """

        # Initialize the reasoning model only if not in test mode
        if not is_test and HAS_TRANSFORMERS:
            self.tokenizer = AutoTokenizer.from_pretrained(model)
            self.reasoning_model = AutoModelForCausalLM.from_pretrained(model)

    def add_memory(self, action: Dict):
        """Store action in agent's memory with timestamp"""
        timestamp = datetime.datetime.now().isoformat()
        action_record = {
            'timestamp': timestamp,
            'action': action['action'],
            'post_id': action.get('post_id'),
            'reasoning': action.get('reasoning')
        }
        self.memory['actions'].append(action_record)
        
        # Update interaction patterns
        action_type = action['action']
        self.memory['interaction_patterns'][action_type] = \
            self.memory['interaction_patterns'].get(action_type, 0) + 1

    def get_agent_response(self, post):
        """Generate agent response based on persona and post content"""
        # Prepare the action context with emphasis on active engagement
        action_context = "\n".join([
            f"Action: {action.value}\n"
            f"Description: {ActionMetadata.DESCRIPTIONS[action]}\n"
            f"Note: Only choose 'do_nothing' if you genuinely have no interest or expertise in the topic.\n"
            + ("Note: This action requires existing comments on the post.\n" if action in [AgentAction.UPVOTE_COMMENT, AgentAction.DOWNVOTE_COMMENT] else "")
            + ("Note: When choosing this action, you MUST provide a specific comment text.\n" if action == AgentAction.CREATE_COMMENT else "")
            for action in AgentAction
        ])

        # Prepare post data with computed values
        post_data = {
            'title': post.title,
            'url': post.url,
            'text': post.text,
            'upvotes': post.upvotes,
            'comment_count': len(post.comments),
            'comments': post.comments
        }

        # Prepare the prompt with all necessary context
        prompt = self.prompt_template.format(
            persona=self.bio,
            interaction_history=json.dumps(self.memory['interaction_patterns'], indent=2),
            action_context=action_context,
            post=post_data
        )

        for attempt in range(self.max_retries):
            try:
                # Generate reasoning using the DeepSeek model
                inputs = self.tokenizer(prompt, return_tensors="pt")
                outputs = self.reasoning_model.generate(
                    inputs.input_ids,
                    max_length=1000,
                    temperature=self.temperature,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.2
                )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                # Try to find and extract the JSON part of the response
                try:
                    # Look for JSON-like structure
                    start_idx = response.find('{')
                    end_idx = response.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = response[start_idx:end_idx]
                        response_data = json.loads(json_str)
                        
                        # Validate the response has required fields
                        if 'action' in response_data:
                            # For create_comment action, ensure comment_text is provided and non-empty
                            if response_data['action'] == AgentAction.CREATE_COMMENT.value:
                                comment_text = response_data.get('comment_text', '').strip()
                                if not comment_text:  # If no comment text or empty string
                                    # Generate a specific comment based on the agent's persona and post content
                                    comment_prompt = f"""
                                    As a {self.bio}, write a specific, concrete comment (max 500 chars) about this post:
                                    Title: {post.title}
                                    Content: {post.text}
                                    Your comment should reflect your expertise and add value to the discussion.
                                    """
                                    comment_inputs = self.tokenizer(comment_prompt, return_tensors="pt")
                                    comment_outputs = self.reasoning_model.generate(
                                        comment_inputs.input_ids,
                                        max_length=500,
                                        temperature=0.7,
                                        do_sample=True
                                    )
                                    comment_text = self.tokenizer.decode(comment_outputs[0], skip_special_tokens=True)[:500]
                                    response_data['comment_text'] = comment_text.strip()
                                
                                # Set comment_id to current number of comments
                                response_data['comment_id'] = len(post.comments)
                            
                            # Validate comment-related actions
                            elif response_data['action'] in [AgentAction.UPVOTE_COMMENT.value, AgentAction.DOWNVOTE_COMMENT.value]:
                                # If there are no comments, retry with a different action
                                if not post.comments:
                                    continue
                                # If comment_id is not provided or invalid, retry
                                comment_id = response_data.get('comment_id')
                                if comment_id is None or comment_id >= len(post.comments):
                                    continue
                            
                            # Add the response to memory
                            self.add_memory(response_data)
                            return response_data
                except json.JSONDecodeError:
                    continue

            except Exception as e:
                if attempt == self.max_retries - 1:
                    # On final attempt, return a random action instead of do_nothing
                    import random
                    # Only include valid actions based on post state
                    valid_actions = [a.value for a in AgentAction if a != AgentAction.DO_NOTHING 
                                   and a != AgentAction.CREATE_COMMENT  # Don't randomly choose create_comment
                                   and (a not in [AgentAction.UPVOTE_COMMENT, AgentAction.DOWNVOTE_COMMENT] 
                                       or len(post.comments) > 0)]
                    return {
                        "action": random.choice(valid_actions),
                        "reasoning": f"Failed to parse model response after {self.max_retries} attempts. Choosing random valid action.",
                        "comment_text": None,
                        "comment_id": None
                    }
                continue

        # If all retries failed, return a random valid action
        import random
        valid_actions = [a.value for a in AgentAction if a != AgentAction.DO_NOTHING 
                        and a != AgentAction.CREATE_COMMENT  # Don't randomly choose create_comment
                        and (a not in [AgentAction.UPVOTE_COMMENT, AgentAction.DOWNVOTE_COMMENT] 
                             or len(post.comments) > 0)]
        return {
            "action": random.choice(valid_actions),
            "reasoning": "Failed to generate valid response after multiple attempts. Choosing random valid action.",
            "comment_text": None,
            "comment_id": None
        }

    def run(self, post):
        """Main execution method for the agent"""
        if not self.is_active:
            return None
        
        response = self.get_agent_response(post)
        return response
