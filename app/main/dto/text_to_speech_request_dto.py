from pydantic import BaseModel
from dto.speakers import SpeakersForAmazonPolly

class TextToSpeechRequestDTO(BaseModel):
    text: str
    voice_id: SpeakersForAmazonPolly = SpeakersForAmazonPolly.MATTHEW