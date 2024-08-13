from enum import Enum


class DocumentFormat(Enum):
    PDF = 'pdf'

class DocumentDTO:
    def __init__(self, name: str, format: DocumentFormat, url: str):
        self.name = name
        self.format = format
        self.url = url

def document_to_dict(dto: DocumentDTO) -> dict:
    return {
        'name': dto.name,
        'format': dto.format.value,
        'url': dto.url,
    }
