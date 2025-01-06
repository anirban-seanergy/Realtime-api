from openai import AsyncOpenAI
import asyncio
from FinalAgentDev.functionalities import tools

from OpenAIExample.audio_util import CHANNELS, SAMPLE_RATE
import base64


class RealtimeApp:

    def __init__(self):
        self.client = AsyncOpenAI()

    async def on_mount(self) -> None:
        await self.handle_realtime_connection()


    async def handle_realtime_connection(self) -> None:

        """
        This function is the main function for the file where the agent is being intereacted with
        it is demo typeish, the development needs to doen to iterate over the responses, and also have an audio agent to smoothen the interaction
        """

        async with self.client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
            
            await connection.session.update(session={'modalities': ['audio']})

            await connection.session.update(session={"turn_detection": {"type": "server_vad"}})

            await connection.session.update(session={
                'tools': tools,
                "tool_choice": "auto",
            })

            prompts = [
                {
                    "prompt": "Book an appointment for John Doe with Dr. Smith in Cardiology on 2025-01-15 at 4pm.",
                    "type": "book_appointment"
                },
                {
                    "prompt": "Update appointment ID 12345 to 2025-01-16 at 5pm.",
                    "type": "update_appointment"
                },
                {
                    "prompt": "Cancel appointment ID 12345 because the patient is unavailable.",
                    "type": "cancel_appointment"
                }
            ]

            for functionality in prompts:
                # Send the prompt as a message
                await connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": functionality["prompt"]}],
                    }
                )

                # Generate a response from the model
                await connection.response.create()

                # Process the response
                async for event in connection:
                    if event.type == 'response.text.delta':
                        # Ignore intermediate delta events
                        continue

                    elif event.type == 'response.text.done':
                        # Ignore completion event
                        continue

                    elif event.type == "response.done":
                        # Extract output for the specific functionality
                        output_type = event.response.output[0].type
                        output_name = event.response.output[0].name
                        output_arguments = event.response.output[0].arguments
                        call_id = event.response.output[0].call_id

                        print(f"Functionality: {functionality['type']}")
                        print(f"Output Type: {output_type}")
                        print(f"Function Name: {output_name}")
                        print(f"Arguments: {output_arguments}")
                        print(f"Call ID: {call_id}")
                        break

    async def send_mic_audio(self) -> None:
        import sounddevice as sd  # type: ignore

        sent_audio = False

        device_info = sd.query_devices()
        print(device_info)

        read_size = int(SAMPLE_RATE * 0.02)

        stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
        )
        stream.start()

        status_indicator = self.query_one(AudioStatusIndicator)

        try:
            while True:
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                await self.should_send_audio.wait()
                status_indicator.is_recording = True

                data, _ = stream.read(read_size)

                connection = await self._get_connection()
                if not sent_audio:
                    asyncio.create_task(connection.send({"type": "response.cancel"}))
                    sent_audio = True

                await connection.input_audio_buffer.append(audio=base64.b64encode(cast(Any, data)).decode("utf-8"))

                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop()
            stream.close()


if __name__ == "__main__":
    app = RealtimeApp()
    asyncio.run(app.on_mount())

