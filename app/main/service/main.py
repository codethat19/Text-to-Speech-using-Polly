from fastapi import FastAPI
import boto3
import base64
from io import BytesIO
from pydub import AudioSegment
import os
import sys

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python module search path
sys.path.append(parent_dir)

from configs.speaker_details import SPEAKER_DETAILS_POLLY
from dto.text_to_speech_request_dto import TextToSpeechRequestDTO
from dto.conversation_request_dto import ConversationRequestDTO
from resource.utilities import create_merged_audio_stream, save_temp_wav_file, create_base64_string_from_wave_file


polly_client = boto3.Session(
                aws_access_key_id="YOUR_AWS_ACCESS_KEY",                     
                aws_secret_access_key="YOUR_AWS_SECRET_ACCESS_KEY",
                region_name='us-west-2').client('polly')

app = FastAPI(
    title="Text to speech using Amazon Polly",
    description="This is an example API built with FastAPI to support text to speech conversion using Amazon Polly",
    version="0.8.0",
    contact={
        "name": "Aayush",
        "url": "https://www.aayushrastogi.com/",
        "email": "aayushrastogi1997@gmail.com",
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
    return SPEAKER_DETAILS_POLLY

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
    response = polly_client.synthesize_speech(
        Text = input.text,
        OutputFormat = 'mp3',
        VoiceId = input.voice_id.value,
        Engine = 'neural'
    )

    audio_stream = response['AudioStream'].read()
    base64_audio = base64.b64encode(audio_stream).decode('utf-8')

    with open("audio.mp3", "wb") as audio_file:
        audio_file.write(audio_stream)

    return {"audio_base64": base64_audio}

@app.post("/generate_conversation")
def create_conversation_from_prompts(input: ConversationRequestDTO):
    """
    Generates a conversation for a list of texts along with their speaker ids
    
    Parameters:
    - **List of JSON objects containing **speaker_id** key and **text** key**

    Returns:
    - **base64_audio**: Base64 string of the generated conversation audio
    """
    audio_bytes = []
    speaker_ids = []

    for conversation_line in input.conversation_list:
        speaker_ids.append(conversation_line.voice_id.value)

        response = polly_client.synthesize_speech(
            Text = conversation_line.text,
            OutputFormat = 'mp3',
            VoiceId = conversation_line.voice_id.value,
            Engine = 'neural'
        )

        audio_stream = response['AudioStream'].read()
        base64_audio = base64.b64encode(audio_stream).decode('utf-8')
        audio_bytes.append(base64_audio)

    # merged_audio_stream, num_channels, sample_width, sample_rate = create_merged_audio_stream(audio_bytes, speaker_ids)
    combined_base64_string = combine_audio_polly(audio_bytes, speaker_ids)
    return combined_base64_string


def combine_audio_polly(base64_audio_list: list, speaker_ids: list):
    # Convert Base64 encoded audio strings to AudioSegment objects
    audio_segments = []

    for base64_audio in base64_audio_list:
        audio_bytes = base64.b64decode(base64_audio)
        audio_segment = AudioSegment.from_file(BytesIO(audio_bytes))
        audio_segments.append(audio_segment)
    
    # Add silence between each audio segment
    combined_audio = audio_segments[0]
    i = 0
    for audio_segment in audio_segments[1:]:
        silence = AudioSegment.silent(duration=300) # 300ms silence for different speakers
        if (i + 1 < len(speaker_ids) and speaker_ids[i + 1] == speaker_ids[i]):
                silence = AudioSegment.silent(duration=200)  # 200ms silence for same speaker
        combined_audio += silence + audio_segment
        i += 1
    
    # Export the combined audio to a byte array
    output_buffer = BytesIO()
    combined_audio.export(output_buffer, format='wav')
    audio_bytearray = output_buffer.getvalue()
    
    # Return the combined audio as a Base64 encoded string
    base64_combined_audio = base64.b64encode(audio_bytearray).decode('utf-8')
    return base64_combined_audio