from fastapi import FastAPI
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from service.tts_service import TextToSpeechService
from dto.text_to_speech_request_dto import TextToSpeechRequestDTO
from dto.conversation_request_dto import ConversationRequestDTO

#Load user configs
USER_CONFIGS = {}
def load_user_configs():
    json_file_path = os.path.join(parent_dir, 'configs/user_configs.json')
    global USER_CONFIGS
    with open(json_file_path, 'r') as json_file:
        USER_CONFIGS = json.load(json_file)
load_user_configs()

app = FastAPI(
    title = USER_CONFIGS["app_information"]["title"],
    description = USER_CONFIGS["app_information"]["description"],
    version = USER_CONFIGS["app_information"]["version"],
    contact = {
        "name": USER_CONFIGS["contact_details"]["name"],
        "url": USER_CONFIGS["contact_details"]["url"],
        "email": USER_CONFIGS["contact_details"]["email"],
    },
)

@app.get("/get_speaker_details")
def get_polly_speaker_details():
    """
    Returns the list of speaker ids supported for the model
    
    Parameters:
    - **model**: Model for which speaker ids are required
    
    Returns:
    - **speaker_details**: Speaker details for the respective text to speech model
    """
    return TextToSpeechService.get_polly_speaker_details()


@app.post("/convert_text_to_speech")
def convert_text_to_speech(input: TextToSpeechRequestDTO):
    """
    Converts text into speech using Amazon Polly
    
    Parameters:
    - **text**: Input text which needs to be converted into speech
    - **voice_id**: Voice id of the speaker
    
    Returns:
    - **base64_audio**: Base64 string of the generated audio
    """
    return TextToSpeechService.convert_text_to_speech(input)


@app.post("/generate_conversation")
def create_conversation_from_prompts(input: ConversationRequestDTO):
    """
    Generates a conversation for a list of texts along with their speaker ids
    
    Parameters:
    - **List of JSON objects containing **speaker_id** key and **text** key**

    Returns:
    - **base64_audio**: Base64 string of the generated conversation audio
    """
    return TextToSpeechService.create_conversation_from_prompts(input)