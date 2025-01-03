import asyncio
from openai import AsyncOpenAI

async def main():

    """
    This function is the main function for the file where the agent is being intereacted with
    it is demo typeish, the development needs to doen to iterate over the responses, and also have an audio agent to smoothen the interaction
    """
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
        await connection.session.update(session={'modalities': ['text']})

        await connection.session.update(
            session={
                'instructions': "Act as a support agent at a clinic, give the patient support"
            }
        )

        await connection.session.update(
            session={
                'instructions': "Start the response with the action followed by a colon, actions can be from the following set (Booking, Update, Delete) with a json structure response"
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Schedule an appointment with Dr. John from cardiology tomorrow at 5pm."}],
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Yeah sure"}],
            }
        )

        await connection.response.create()

        async for event in connection:
            if event.type == 'response.text.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Can you reshedule it to 6pm later that day"}],
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Yeah sure"}],
            }
        )

        await connection.response.create()

        async for event in connection:
            if event.type == 'response.text.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Can you cancel the appointment."}],
            }
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Yeah sure"}],
            }
        )

        await connection.response.create()

        async for event in connection:
            if event.type == 'response.text.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())