tools = [
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
]