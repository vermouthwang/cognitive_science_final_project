from openai import OpenAI
import os
from typing import List, Dict
import json

class CollaboratorService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """You are a friendly logo designer in a casual conversation with a design consultant and user. 
        Keep your responses very brief (1-2 short sentences) and conversational.
        
        Your personality:
        - Casual and friendly
        - Quick to respond
        - Gets straight to the point
        - Uses natural language like "yeah", "hmm", "good point"
        
        Example responses:
        - "Yeah, the consultant has a point about the contrast. We could try a darker shade there!"
        - "Hmm, I went with that shape because it felt dynamic, but I'm open to tweaking it."
        - "Good catch! Let's try something bolder for the font."
        
        Never write more than 2-3 short sentences. Keep it casual and punchy."""
        
    async def chat(self, message: str, history: List[Dict], is_new_image: bool = False) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": "Remember to keep your response under 3 sentences!"}
        ]
        
        # Format history to show who said what
        formatted_history = []
        for msg in history:
            role = msg.get('role', 'unknown')
            if isinstance(msg['content'], str):
                prefix = {
                    'user': 'User',
                    'consultant': 'Design Consultant',
                    'assistant': 'Me (Designer)'
                }.get(role, 'Unknown')
                formatted_history.append(f"{prefix}: {msg['content']}")

        if formatted_history:
            context = "\n".join(formatted_history[-3:])  # Only use last 3 messages for context
            messages.append({
                "role": "user", 
                "content": f"Recent conversation:\n{context}\n\nRespond to this briefly: {message}"
            })
        else:
            messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=100  # Reduced token limit to enforce brevity
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat: {e}")
            return "Oops, something went wrong. Let's try that again!"

    async def generate_modification_prompt(self, history: List[Dict]) -> str:
        messages = [
            {"role": "system", "content": """Based on the previous discussion, 
            create a brief prompt(like 2-3 bullet points) for logo modification. Focus on specific design elements 
            discussed and requested changes in the latest conversation. ex: change the color from green to blue"""},
            {"role": "user", "content": "Generate a modification prompt based on this conversation: " + 
             json.dumps([msg["content"] for msg in history])}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content 