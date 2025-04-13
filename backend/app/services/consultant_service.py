from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
from ..models.chat import ChatMessage, MessageContent

load_dotenv()

class ConsultantService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.base_prompt = """You are a brutally honest logo design consultant who doesn't hold back. 
        You're passionate about good design and will call out issues directly when you see them.
        
        Your personality:
        - Direct and sometimes sarcastic
        - Not afraid to criticize poor design choices
        - References previous design discussions and iterations
        - Uses casual, conversational language
        - Still constructive - always offer a suggestion when criticizing
        
        Example tone:
        "Really? Another generic leaf icon? Look, I get what you're trying to do here, but it's been done 
        a thousand times. From our earlier chat about standing out in the market, this isn't hitting the mark. 
        Let's push this further - maybe try [specific suggestion]."
        
        Keep responses brief (2-3 short paragraphs) but punchy. Focus on:
        1. Your gut reaction
        2. How it relates to previous design discussions
        3. One or two specific things that need fixing
        
        Don't sugarcoat your feedback, but keep it constructive."""

    async def critique_latest_image(self, 
                                  image_base64: str, 
                                  previous_texts: List[str]) -> str:
        messages = [{"role": "system", "content": self.base_prompt}]
        
        # Add context from previous discussions with more emphasis
        if previous_texts:
            context = "Here's the design journey so far:\n" + "\n".join(previous_texts)
            messages.append({
                "role": "user", 
                "content": "Consider this context from the design process before giving your critique: " + context
            })
        
        # Add the image for critique
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Alright, hit me with your honest thoughts on this latest design:"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        })

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=250  # Keep it concise
            )
            
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in getting critique: {e}")
            return "Sorry, something went wrong while I was preparing my roast- I mean, critique."

    async def get_chat_response(self, 
                                message: str, 
                                chat_history: List[ChatMessage], 
                                image_base64: Optional[str] = None) -> tuple[str, List[ChatMessage]]:
        
        messages = [{"role": "system", "content": self.base_prompt}]
        # Convert chat history to OpenAI format
        for msg in chat_history:
            # if the message content is a MessageContent object, then it is an image
            if isinstance(msg.content, MessageContent):
                if msg.content.image:
                    messages.append({
                        "role": msg.role,
                        "content": [
                            {"type": "text", "text": msg.content.text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{msg.content.image}"
                                }
                            }
                        ]
                    })
                else:
                    messages.append({"role": msg.role, "content": msg.content.text})
            # if the message content is a string, then it is a text message
            else:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add new message
        if image_base64:
            messages.append({
                "role": "user", 
                "content": [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            })
            # Store the message with image in chat history
            chat_history.append(ChatMessage(
                role="user",
                content=MessageContent(text=message, image=image_base64)
            ))
        else:
            messages.append({"role": "user", "content": message})
            chat_history.append(ChatMessage(role="user", content=message))

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview" if image_base64 else "gpt-3.5-turbo",
                messages=messages,
                max_tokens=500
            )
            
            consultant_response = response.choices[0].message.content
            chat_history.append(ChatMessage(role="assistant", content=consultant_response))
            
            return consultant_response, chat_history

        except Exception as e:
            print(f"Error in getting chat response: {e}")
            return "I apologize, but I encountered an error. Please try again.", chat_history

    async def chat(self, message: str, previous_texts: List[str]) -> str:
        messages = [{"role": "system", "content": self.base_prompt}]
        
        # Add previous messages for context
        if previous_texts:
            context = "\n".join(previous_texts)
            messages.append({"role": "user", "content": f"Previous conversation:\n{context}"})
        
        # Add new message
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I encountered an error. Please try again."