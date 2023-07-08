import base64
import io
import os
import wave
import struct

def create_merged_audio_stream(base64_audio_list, speaker_ids):
    # Audio parameters
    sample_rate = 44100  # Sample rate in Hz
    silence_duration = 0.3  # Duration of silence in seconds
    # print(type(base64_audio_list[0]))

    #Speaker details:
    # speaker_ids = [1, 2, 1, 1]
    j = 1
    # Create an in-memory byte stream to store the merged audio
    merged_audio_stream = io.BytesIO()

    # Iterate over each base64 audio string
    for i, base64_audio in enumerate(base64_audio_list):
        # Decode the base64 audio string to bytes
        audio_bytes = base64.b64decode(base64_audio)
        
        # Create a temporary in-memory byte stream for the current audio segment
        temp_audio_stream = io.BytesIO(audio_bytes)
        
        print(type(temp_audio_stream))
        # print(temp_audio_stream)
        # Read the audio data using the wave module
        with wave.open(temp_audio_stream, 'rb') as temp_wave:
            num_channels = temp_wave.getnchannels()
            sample_width = temp_wave.getsampwidth()
            frames = temp_wave.readframes(temp_wave.getnframes())

            # Write the audio data to the merged audio stream
            if i > 0:
                silence_duration = 0.3
                # print(len(speaker_ids))
                if (j + 1 <= len(speaker_ids)):
                    print(j)
                    # j += 1
                    if speaker_ids[j - 1] == speaker_ids[j]:
                        # print(j)
                        silence_duration = 0.2
                    j += 1
                    
                        
                # Append 2 seconds of silence before the current audio segment
                num_silence_frames = int(sample_rate * silence_duration)
                silence_bytes = struct.pack('<h', 0) * num_silence_frames * num_channels * sample_width
                merged_audio_stream.write(silence_bytes)

            merged_audio_stream.write(frames)
    return [merged_audio_stream, num_channels, sample_width, sample_rate]

def save_temp_wav_file(merged_audio_stream, num_channels, sample_width, sample_rate):
    # Save the merged audio to a WAV file
    output_file = "output.wav"
    merged_audio_data = merged_audio_stream.getvalue()

    with wave.open(output_file, 'wb') as wave_file:
        wave_file.setnchannels(num_channels)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(merged_audio_data)

    with open('output.wav', 'rb') as wav_file:
        wav_data = wav_file.read()

    os.remove(output_file)
    return wav_data

def create_base64_string_from_wave_file(wav_data):
    # Encode the merged audio data to base64
    merged_base64 = base64.b64encode(wav_data).decode('utf-8')
    file_path = "output.txt"

    with open(file_path, 'w') as file:
        file.write(merged_base64)