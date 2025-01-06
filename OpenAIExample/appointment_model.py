import sqlite3
from datetime import datetime, timedelta
import random
import string

class AppointmentDBHandler:
    def __init__(self, db_name="hospital.db"):
        """Initialize the database handler with the specified db name and create tables."""
        self.connection = sqlite3.connect(db_name)  # Connect to SQLite database
        self.cursor = self.connection.cursor()      # Create a cursor object for executing SQL queries
        self._create_tables()                       # Create tables if they don't exist

    def _create_tables(self):
        """Create tables if they do not exist."""

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                contact INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id TEXT PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
            );
        """)

        self.connection.commit()

    def add_patient(self, name, age, contact):
        self.cursor.execute("""
            SELECT patient_id FROM patients WHERE name = ? AND contact = ?
        """, (name, contact))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            patient_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.cursor.execute("""
                INSERT INTO patients (patient_id, name, age, contact) VALUES (?, ?, ?, ?)
            """, (patient_id, name, age, contact))
            self.connection.commit()
            return self.cursor.lastrowid

    def add_doctor(self, name, specialization):
        self.cursor.execute("""
            SELECT doctor_id FROM doctors WHERE name = ? AND specialization = ?
        """, (name, specialization))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            doctor_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.cursor.execute("""
                INSERT INTO doctors (doctor_id, name, specialization) VALUES (?, ?, ?)
            """, (doctor_id, name, specialization))
            self.connection.commit()
            return self.cursor.lastrowid

    def get_doctor_id(self, name: str, specialization: str) -> int:
        self.cursor.execute("""
            SELECT doctor_id FROM doctors WHERE name = ? AND specialization = ?
        """, (name, specialization))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def get_available_appointments(self, doctor_id: int, date: str):
        """
        Get all available 1-hour appointment slots for a doctor on a given date.
        """

        # Define working hours and lunch break
        work_start = datetime.strptime(f"{date} 09:00:00", "%Y-%m-%d %H:%M:%S")
        work_end = datetime.strptime(f"{date} 17:00:00", "%Y-%m-%d %H:%M:%S")
        lunch_start = datetime.strptime(f"{date} 12:00:00", "%Y-%m-%d %H:%M:%S")
        lunch_end = datetime.strptime(f"{date} 13:00:00", "%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
            SELECT appointment_date
            FROM appointments
            WHERE doctor_id = ? AND appointment_date LIKE ?
        """, (doctor_id, f"{date}%"))
        scheduled_appointments = self.cursor.fetchall()

        scheduled_times = set(
            [datetime.strptime(app[0], "%Y-%m-%d %H:%M:%S") for app in scheduled_appointments]
        )

        available_slots = []
        current_time = work_start

        while current_time < work_end:

            if lunch_start <= current_time < lunch_end:
                current_time = lunch_end
                continue

            if current_time not in scheduled_times:
                available_slots.append(current_time)

            current_time += timedelta(hours=1)

        return available_slots

    def get_appointment_by_patient(self, patient_id: int) -> list:
        """
        Get the appointment details for a patient.
        
        parameters:
        - `patient_id`: int -> id of the patient with existing appointment
        """

        self.cursor.execute("""
            SELECT appointment_date, doctor_id FROM appointments WHERE patient_id = ?
        """, (patient_id,))
        return self.cursor.fetchone()
    
    def get_patient_by_contact(self, contact: int) -> list:
        """
        Get patient by their contact number.
        
        parameters:
        - `contact`: int -> Number of the patient
        """
        self.cursor.execute("SELECT patient_id, name FROM patients WHERE contact = ?", (contact,))
        return self.cursor.fetchone()
    
    def reschedule_appointment(self, contact: int, new_appointment_date: str) -> str:
        """
        Reschedule an appointment for a patient identified by contact number.

        parameters:
        - `contact`: int -> number associated with the patient who has existing appointment date
        - `new_appointment_date`: str -> new date of appoinment to which the appointment is to be rescheduled
        """

        patient = self.get_patient_by_contact(contact)
        if not patient:
            return "Patient with this contact number not found."
        
        patient_id = patient[0]
        patient_name = patient[1]

        existing_appointment = self.get_appointment_by_patient(patient_id)
        if not existing_appointment:
            return f"No appointment found for patient {patient_name}."

        doctor_id = existing_appointment[1]

        formated_appointment_date = convert_to_standard_format(new_appointment_date)
        if formated_appointment_date:
            available_appointments = self.get_available_appointments(doctor_id, formated_appointment_date[:10])
        else:
            return f"{new_appointment_date} -  is not supported"

        if not any(appointment.strftime("%Y-%m-%d %H:%M:%S") == new_appointment_date for appointment in available_appointments):
            return f"Doctor is not available at {new_appointment_date}."

        self.cursor.execute("""
            UPDATE appointments
            SET appointment_date = ?
            WHERE patient_id = ? AND doctor_id = ?
        """, (new_appointment_date, patient_id, doctor_id))
        self.connection.commit()

        return f"Appointment for {patient_name} has been successfully rescheduled to {new_appointment_date}."

    def schedule_appointment(self, patient_id: int, doctor_id: int, appointment_date: str) -> str:
        """
        Check if a doctor is available on the given date and schedule an appointment.

        Parameters:
        - `patient_id`: int -> Id of the patient
        - `doctor_id`: int -> Id of the doctor
        - `appointment_date`:str -> Date of the appointment
        """

        try:
            # Validate the date format using a utility function
            appointment_date = convert_to_standard_format(appointment_date)
        except ValueError:
            return "Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'."

        # Check if the doctor is already scheduled at this date and time
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE doctor_id = ? AND appointment_date = ?
        """, (doctor_id, appointment_date))
        result = self.cursor.fetchone()

        if result[0] > 0:
            return f"Doctor with ID {doctor_id} is not available at {appointment_date}."
        else:
            appointment_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            try:
                self.cursor.execute("""
                    INSERT INTO appointments (appointment_id, patient_id, doctor_id, appointment_date)
                    VALUES (?, ?, ?, ?)
                """, (appointment_id, patient_id, doctor_id, appointment_date))
                self.connection.commit()
                return f"Appointment scheduled successfully with ID {appointment_id} for Patient ID {patient_id} with Doctor ID {doctor_id} on {appointment_date}."
            except Exception as e:
                return f"Failed to schedule appointment: {str(e)}"
    # Close the database connection
    def close(self):
        self.connection.close()

    def add_appointment(self, patient_id: int, doctor_id: int, appointment_date: str) -> None:
        """
        Add an appointment to the database for a specific patient and doctor at a given time.
        
        :param patient_id: ID of the patient
        :param doctor_id: ID of the doctor
        :param appointment_date: The date and time of the appointment in 'YYYY-MM-DD HH:MM:SS' format
        """
        self.cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date)
            VALUES (?, ?, ?)
        """, (patient_id, doctor_id, appointment_date))

        self.connection.commit()
        
        print(f"Appointment scheduled successfully for Patient ID {patient_id} with Doctor ID {doctor_id} on {appointment_date}.")

def convert_to_standard_format(input_date: str) -> str:

    supported_formats = [
        "%Y-%m-%d %H:%M:%S",       # Example: 2025-10-10 16:00:00
        "%Y-%m-%d %I:%M:%S %p",    # Example: 2025-10-10 4:00:00 PM
        "%Y-%m-%d %I:%M %p",       # Example: 2025-10-10 4:00 PM
        "%d/%m/%Y %H:%M:%S",       # Example: 10/10/2025 16:00:00
        "%d-%m-%Y %H:%M:%S",       # Example: 10-10-2025 16:00:00
        "%d/%m/%Y %I:%M:%S %p",    # Example: 10/10/2025 4:00:00 PM
        "%d-%m-%Y %I:%M:%S %p",    # Example: 10-10-2025 4:00:00 PM
        "%d/%m/%Y %I:%M %p",       # Example: 10/10/2025 4:00 PM
        "%d-%m-%Y %I:%M %p",       # Example: 10-10-2025 4:00 PM
        "%B %d, %Y %I:%M %p",      # Example: October 10, 2025 4:00 PM
        "%d %B %Y %I:%M %p",       # Example: 10 October 2025 4:00 PM
        "%Y-%m-%dT%H:%M",          # Example: 2025-10-10T16:00
        "%Y-%m-%dT%I:%M%p",        # Example: 2025-10-10T4:00PM
    ]

    for fmt in supported_formats:
        try:
            date_obj = datetime.strptime(input_date, fmt)
            
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If the current format fails, continue with the next format
            continue
    return None

if __name__ == "__main__":

    # Initialize the database handler
    db_handler = AppointmentDBHandler()

    # Add some patients
    patient_1 = db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
    patient_2 = db_handler.add_patient(name="Jane Smith", age=25, contact=9876543210)

    # Add some doctors
    doctor_1 = db_handler.add_doctor(name="Dr. Alice", specialization="Cardiologist")
    doctor_2 = db_handler.add_doctor(name="Dr. Bob", specialization="Dermatologist")

    # Fetch the IDs of the doctors (useful for scheduling)
    doctor_1_id = db_handler.get_doctor_id(name="Dr. Alice", specialization="Cardiologist")
    doctor_2_id = db_handler.get_doctor_id(name="Dr. Bob", specialization="Dermatologist")

    # Schedule appointments
    appointment_1 = db_handler.schedule_appointment(
        patient_id=patient_1,
        doctor_id=doctor_1_id,
        appointment_date="2025-01-05 10:00:00"
    )

    appointment_2 = db_handler.schedule_appointment(
        patient_id=patient_2,
        doctor_id=doctor_2_id,
        appointment_date="2025-01-05 11:00:00"
    )

    # Try scheduling an appointment for an already booked time slot
    appointment_3 = db_handler.schedule_appointment(
        patient_id=patient_1,
        doctor_id=doctor_1_id,
        appointment_date="2025-01-05 10:00:00"
    )  # Should return a "Doctor not available" message.

    # Reschedule an appointment
    reschedule_result = db_handler.reschedule_appointment(
        contact=1234567890,
        new_appointment_date="2025-01-06 14:00:00"
    )

    # Fetch all available appointment slots for a doctor on a specific date
    available_slots = db_handler.get_available_appointments(
        doctor_id=doctor_1_id,
        date="2025-01-06"
    )
    print("Available Slots:", [slot.strftime("%Y-%m-%d %H:%M:%S") for slot in available_slots])

    # Fetch appointment details for a patient
    patient_appointments = db_handler.get_appointment_by_patient(patient_id=patient_1)
    print(f"Appointments for Patient ID {patient_1}:", patient_appointments)

    # Fetch patient details by contact number
    patient_details = db_handler.get_patient_by_contact(contact=1234567890)
    print("Patient Details:", patient_details)

    # Close the database connection
    db_handler.close()