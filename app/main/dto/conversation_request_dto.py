from pydantic import BaseModel
from typing import List
from dto.text_to_speech_request_dto import TextToSpeechRequestDTO

class ConversationRequestDTO(BaseModel):
    conversation_list: List[TextToSpeechRequestDTO]