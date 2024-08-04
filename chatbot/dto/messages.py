import json

from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    # user — The human that is sending messages to the model
    # assistant — The model that is sending messages back to the human user
    USER = 'user'
    ASSISTANT = 'assistant'


class MessageDTO:
    def __init__(self, conversation_id: str, role: MessageRole, created_at: datetime, text: str):
        self.conversation_id = conversation_id
        self.created_at = created_at
        self.role = role
        self.text = text

    def __str__(self) -> str:
        return json.dumps({
            'conversation_id': self.conversation_id,
            'created_at': self.created_at.isoformat(),
            'role': self.role.value,
            'text': self.text,
        })
