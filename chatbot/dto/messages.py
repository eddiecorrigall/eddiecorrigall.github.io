from datetime import datetime
from enum import Enum
from typing import List

from dto.document import DocumentDTO, document_to_dict


class MessageRole(Enum):
    # user — The human that is sending messages to the model
    # assistant — The model that is sending messages back to the human user
    USER = 'user'
    ASSISTANT = 'assistant'

class MessageDTO:
    def __init__(
        self,
        conversation_id: str,
        role: MessageRole,
        created_at: datetime,
        text: str,
        documents: List[DocumentDTO] = None,
    ):
        self.conversation_id = conversation_id
        self.created_at = created_at
        self.role = role
        self.text = text
        self.documents = documents

def message_to_dict(dto: MessageDTO) -> dict:
    result = {
        'conversation_id': dto.conversation_id,
        'created_at': dto.created_at.isoformat(),
        'role': dto.role.value,
        'text': dto.text,
    }
    if dto.documents:
        result['documents'] = [
            document_to_dict(document_dto)
            for document_dto in dto.documents
        ]
    return result
