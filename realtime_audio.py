import asyncio
from  openai import AsyncOpenAI

import base64

def encode_mp3_to_base64(file_path):
    """
    Encodes an MP3 file to a Base64 string.
    
    :param file_path: Path to the MP3 file.
    :return: Base64 encoded string.
    """
    try:
        with open(file_path, "rb") as mp3_file:
            # Read the file content
            file_data = mp3_file.read()
            
            # Encode the binary data to base64
            base64_data = base64.b64encode(file_data).decode('utf-8')
            
            return base64_data
    except Exception as e:
        print(f"Error encoding file: {e}")
        return None


async def main():
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
        await connection.session.update(session={'modalities': ['audio']})

        await connection.session.update(
            session={
                'instructions': "Act as a support agent at a clinic, give the patient support"
            }
        )

        await connection.session.update(
            session={
                'instructions': """
                                    Give the output in the following format:
                                    {"doctor": "", "department": "", "date": "", "time": ""}    
                                """
            }
        )

        await connection.session.update(
            session={
                'instructions': "Start the response with the action followed by a colon, actions can be from the following set (Booking, Update, Delete) with a json structure response"
            }
        )

        await connection.session.update(
            session={
                "tools": [
                    {
                        "type": "function",
                        "name": "generate_horoscope",
                        "description": "Give today's horoscope for an astrological sign.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "sign": {
                            "type": "string",
                            "description": "The sign for the horoscope.",
                            "enum": [
                                "Aries",
                                "Taurus",
                                "Gemini",
                                "Cancer",
                                "Leo",
                                "Virgo",
                                "Libra",
                                "Scorpio",
                                "Sagittarius",
                                "Capricorn",
                                "Aquarius",
                                "Pisces"
                            ]
                            }
                        },
                        "required": ["sign"]
                        }
                    }
                ],
                "tool_choice": "auto"
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_audio_buffer.append", "audio": encode_mp3_to_base64("input_1.mp3")}],
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_audio_buffer.append", "audio": encode_mp3_to_base64("affirmation.mp3")}],
            }
        )

        await connection.response.create()

        async for event in connection:
            if event.type == 'response.audio_transcript.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())