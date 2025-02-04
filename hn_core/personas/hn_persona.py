from markdownify import markdownify as md


class HNPersona:
    def __init__(self, users: dict, items: dict, template: str):
        self.users = users
        self.items = items
        self.template = template
        
    def get_prompt(self, user_id: str):
        self.user = {}
        self.user_data = self._get_user_data(user_id)

        self._basic_metrics()
        self._comments_examples()
        self._posts_examples()
        
        prompt = self._get_prompt()

        return prompt

    def _get_user_data(self, user_id):
        user = self.users[user_id].copy()  # Create a copy to avoid modifying original
        
        # Replace submitted list with items and their root stories
        processed_items = []
        for item_id in user['submitted']:
            item_id_str = str(item_id)
            if item_id_str in self.items:
                item = self.items[item_id_str]
                if item.get('type') == 'comment':
                    root_story = self.get_root_story(item_id)
                    # Check if parent is a story or another comment
                    parent_item = self.items.get(str(item.get('parent')))
                    is_direct_reply = parent_item and parent_item.get('type') != 'comment'
                    
                    if root_story:
                        processed_items.append({
                            'comment': item,
                            'root_story': root_story,
                            'is_direct_reply': is_direct_reply
                        })
                else:
                    processed_items.append(item)
        
        user['submitted'] = processed_items
        return user

    def get_root_story(self, item_id):
        item = self.items.get(str(item_id))
        if not item or 'parent' not in item:
            return item
        return self.get_root_story(item['parent'])

    def _basic_metrics(self):
        self.user['karma'] = self.user_data.get('karma', None)
        self.user['about'] = md(self.user_data['about']).strip() if self.user_data.get('about') else None

        submitted = self.user_data.get('submitted', [])
        self.user['direct_comments_count'] = sum(1 for item in submitted 
            if isinstance(item, dict) and 'comment' in item and not item['comment'].get('dead') and item.get('is_direct_reply', False))
        self.user['total_comments_count'] = sum(1 for item in submitted 
            if isinstance(item, dict) and 'comment' in item and not item['comment'].get('dead'))
        self.user['indirect_comments_count'] = self.user['total_comments_count'] - self.user['direct_comments_count']
        self.user['posts_count'] = sum(1 for item in submitted if item.get('type') == 'story' and not item.get('dead'))

    def _comments_examples(self, n: int = 10):
        comments = [
            item for item in self.user_data['submitted'] 
            if isinstance(item, dict) and 
            (('type' in item and item.get('type') == 'comment') or 'comment' in item) and 
            not (item.get('dead') if 'type' in item else item['comment'].get('dead'))
        ]
        self.user['comments_examples'] = comments[:n]

    def _posts_examples(self, n: int = 10):
        posts = [item for item in self.user_data['submitted'] if item.get('type') == 'story' and not item.get('dead')]
        self.user['posts_examples'] = posts[:n]

    def _get_prompt(self):
        # Format direct reply comments with their root stories
        comments_formatted = []
        count = 0
        for comment in self.user['comments_examples']:
            if isinstance(comment, dict) and 'comment' in comment and comment.get('is_direct_reply'):
                root_story = comment.get('root_story', {})
                comment_text = comment['comment'].get('text', '')
                title = root_story.get('title', '')
                url = root_story.get('url', '')
                story_text = md(root_story['text']).strip() if root_story.get('text') else ''
                
                count += 1
                formatted_comment = (
                    f'<comment_{count}>\n'
                    + (f'<post_title>{title}</post_title>\n' if title else '')
                    + (f'<post_url>{url}</post_url>\n' if url else '') 
                    + (f'<post_text>{story_text}</post_text>\n' if story_text else '')
                    + f'<your_comment>{comment_text}</your_comment>\n'
                    f'</comment_{count}>'
                )
                comments_formatted.append(formatted_comment)
        
        comments_formatted = '\n'.join(comments_formatted)

        # Format the posts
        posts_formatted = []
        count = 0
        for post in self.user['posts_examples']:
            count += 1
            title = post.get('title', '')
            url = post.get('url', '')
            story_text = md(post['text']).strip() if post.get('text') else ''
            formatted_post = (
                f'<post_{count}>\n'
                + (f'<post_title>{title}</post_title>\n' if title else '')
                + (f'<post_url>{url}</post_url>\n' if url else '') 
                + (f'<post_text>{story_text}</post_text>\n' if story_text else '')
                + f'</post_{count}>'
            )
            posts_formatted.append(formatted_post)
        
        posts_formatted = '\n'.join(posts_formatted)

        # Create a mapping of template variables to their values
        replacements = {
            '{{COMMENTS}}': comments_formatted if comments_formatted else 'None',
            '{{POSTS}}': posts_formatted if posts_formatted else 'None',
            '{{ABOUT}}': self.user['about'] if self.user['about'] else 'Not provided',
            '{{COMMENTS_COUNT}}': str(self.user['total_comments_count']),
            '{{DIRECT_COMMENTS_COUNT}}': str(self.user['direct_comments_count']),
            '{{INDIRECT_COMMENTS_COUNT}}': str(self.user['indirect_comments_count']),
            '{{POSTS_COUNT}}': str(self.user['posts_count'])
        }
        
        # Apply all replacements to the template
        prompt = self.template
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)

        return prompt


# Example usage
if __name__ == '__main__':
    import os
    import json
    from hn_core.utils.storage import R2Storage

    # if hn_archive does not exist locally then download it from R2
    if not os.path.exists('hn_archive'):
        os.makedirs("hn_archive")
        storage = R2Storage()
        storage.download_file("hn-archive", "users.json", "hn_archive/users.json")
        storage.download_file("hn-archive", "items.json", "hn_archive/items.json")

    # This is to just get the dicitonary directly from R2 downloading the files 
    # storage = R2Storage()
    # users = storage.get_object('hn-archive', 'users.json')
    # items = storage.get_object('hn-archive', 'items.json')
    users = json.load(open('hn_archive/users.json'))
    items = json.load(open('hn_archive/items.json'))

    # Here is how to get the persona prompt. 
    # TODO: This can then be fed into the Agent class to get the response
    template = open('hn_core/personas/template.txt').read()
    persona = HNPersona(users, items, template)
    user_id = 'tonymet' # wilg
    prompt = persona.get_prompt(user_id)
    print(prompt)

