tools = [
    {
        "type": "function",
        "name": "book_appointment",
        "description": "Schedule a new appointment for a patient, and returns the appointment ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                "type": "string",
                "description": "The unique ID of the patient."
                },
                "doctor_name": {
                "type": "string",
                "description": "The name of the doctor with whom the appointment is being booked."
                },
                "specialization": {
                "type": "string",
                "description": "The department or specialty for the appointment (e.g., Cardiology, Orthopedics)."
                },
                "appointment_date": {
                "type": "string",
                "format": "date",
                "description": "The date and time of the appointment (YYYY-MM-DD HH:MM:SS)."
                }
            },
            "required": ["patient_name", "doctor_name", "specialization", "appointment_date"]
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
                "new_appointment_date": {
                "type": "string",
                "format": "date",
                "description": "The new date for the appointment (YYYY-MM-DD HH:MM:SS)."
                },
            },
            "required": ["appointment_id", "new_appointment_date"]
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
                }
            },
            "required": ["appointment_id"]
            }
    }
]