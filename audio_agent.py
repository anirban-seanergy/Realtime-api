import pyaudio
import base64
import webrtcvad
import time

def base64_encode_audio(data):
    """
    Encode raw audio data to Base64.
    """
    return base64.b64encode(data).decode('utf-8')

def is_speech(data, vad, sample_rate=16000):
    """
    Use WebRTC VAD to determine if the audio contains speech.
    """
    return vad.is_speech(data, sample_rate)

def record_and_encode_with_vad():
    """
    Record audio and encode it to Base64 only when speech is detected.
    """
    # Audio stream parameters
    CHUNK = 320          # Frame size for VAD (20ms for 16kHz audio)
    FORMAT = pyaudio.paInt16  # 16-bit PCM
    CHANNELS = 1          # Mono audio
    RATE = 16000          # Sampling rate (16 kHz, required for WebRTC VAD)

    # Initialize PyAudio and WebRTC VAD
    audio = pyaudio.PyAudio()
    vad = webrtcvad.Vad()
    vad.set_mode(2)  # Aggressiveness mode: 0 (least aggressive) to 3 (most aggressive)

    # Open the audio stream
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording... Speak to start recording. Silence will pause recording.")

    try:
        while True:
            # Read a chunk of audio data
            audio_data = stream.read(CHUNK, exception_on_overflow=False)

            # Check for speech
            if is_speech(audio_data, vad, sample_rate=RATE):
                print("Speech detected!")
                encoded_audio = base64_encode_audio(audio_data)
                print(f"Base64 Encoded Audio: {encoded_audio[:60]}...")  # Print part of the encoded data
            else:
                print("Silence detected. Pausing...")
                time.sleep(0.2)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\nStopped recording.")
    finally:
        # Stop and close the audio stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    record_and_encode_with_vad()