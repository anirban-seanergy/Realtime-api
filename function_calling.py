import asyncio
from openai import AsyncOpenAI

from realtime_audio import encode_mp3_to_base64

async def main():

    """
    This function is the main function for the file where the agent is being intereacted with
    it is demo typeish, the development needs to doen to iterate over the responses, and also have an audio agent to smoothen the interaction
    """
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
        
        await connection.session.update(session={'modalities': ['text']})

        await connection.session.update(session={
            'tools': [
                {
                    "type": "function",
                    "name": "book_appointment",
                    "description": "Schedule a new appointment for a patient.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_name": {
                        "type": "string",
                        "description": "The name of the patient."
                        },
                        "doctor_name": {
                        "type": "string",
                        "description": "The name of the doctor with whom the appointment is being booked."
                        },
                        "department": {
                        "type": "string",
                        "description": "The department or specialty for the appointment (e.g., Cardiology, Orthopedics)."
                        },
                        "date": {
                        "type": "string",
                        "format": "date",
                        "description": "The date of the appointment (YYYY-MM-DD)."
                        },
                        "time": {
                        "type": "string",
                        "format": "time",
                        "description": "The time of the appointment (HH:MM)."
                        }
                    },
                    "required": ["patient_name", "doctor_name", "department", "date", "time"]
                    }
                },
                {
                    "type": "function",
                    "name": "update_appointment",
                    "description": "Modify an existing appointment for a patient.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                        "type": "string",
                        "description": "The unique identifier of the appointment to be updated."
                        },
                        "date": {
                        "type": "string",
                        "format": "date",
                        "description": "The new date for the appointment (YYYY-MM-DD)."
                        },
                        "time": {
                        "type": "string",
                        "format": "time",
                        "description": "The new time for the appointment (HH:MM)."
                        }
                    },
                    "required": ["appointment_id"]
                    }
                },
                {
                    "type": "function",
                    "name": "cancel_appointment",
                    "description": "Cancel an existing appointment for a patient.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                        "type": "string",
                        "description": "The unique identifier of the appointment to be canceled."
                        },
                        "reason": {
                        "type": "string",
                        "description": "The reason for canceling the appointment."
                        }
                    },
                    "required": ["appointment_id"]
                    }
                }
            ],
            "tool_choice": "auto",
        })

        functionalities = [
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

        for functionality in functionalities:
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

asyncio.run(main())