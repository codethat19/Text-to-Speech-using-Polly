from fastapi import FastAPI
import boto3
import base64
from io import BytesIO
from pydub import AudioSegment
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

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

polly_client = boto3.Session(
                aws_access_key_id=USER_CONFIGS["polly_access_ids"]["aws_access_key_id"],                     
                aws_secret_access_key=USER_CONFIGS["polly_access_ids"]["aws_secret_access_key"],
                region_name='us-west-2').client('polly')



class TextToSpeechService():

    def get_polly_speaker_details():
        json_file_path = os.path.join(parent_dir, 'configs/speaker_details.json')
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    

    def convert_text_to_speech(input: TextToSpeechRequestDTO):
        response = polly_client.synthesize_speech(
            Text = input.text,
            OutputFormat = 'mp3',
            VoiceId = input.voice_id.value,
            Engine = 'neural'
        )
        audio_stream = response['AudioStream'].read()
        base64_audio = base64.b64encode(audio_stream).decode('utf-8')
        return {"audio_base64": base64_audio}

    def create_conversation_from_prompts(input: ConversationRequestDTO):
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
        combined_base64_string = TextToSpeechService.combine_audio_polly(audio_bytes, speaker_ids)
        return combined_base64_string

    @staticmethod
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