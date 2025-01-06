import unittest
from datetime import datetime, timedelta
import sqlite3
from appointment_model import AppointmentDBHandler  # Replace with the correct module name

class TestAppointmentDBHandler(unittest.TestCase):

    def setUp(self):
        """
        Set up the in-memory database for each test.
        """
        self.db_handler = AppointmentDBHandler(db_name=":memory:")

    def tearDown(self):
        """
        Tear down the database after each test.
        """
        self.db_handler.close()

    def test_add_patient(self):
        """
        Test adding a patient to the database.
        """
        patient_id = self.db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
        self.assertIsNotNone(patient_id, "Patient ID should not be None.")

    def test_add_doctor(self):
        """
        Test adding a doctor to the database.
        """
        doctor_id = self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        self.assertIsNotNone(doctor_id, "Doctor ID should not be None.")

    def test_get_doctor_id(self):
        """
        Test retrieving a doctor's ID.
        """
        self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        doctor_id = self.db_handler.get_doctor_id(name="Dr. Smith", specialization="Cardiology")
        self.assertIsNotNone(doctor_id, "Doctor ID should not be None.")

    def test_book_appointment(self):
        """
        Test booking an appointment.
        """
        patient_id = self.db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
        self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        appointment_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        result = self.db_handler.book_appointment(
            patient_id=patient_id,
            doctor_name="Dr. Smith",
            specialization="Cardiology",
            appointment_date=appointment_date
        )
        self.assertIn("Appointment scheduled successfully", result)

    def test_get_available_appointments(self):
        """
        Test retrieving available appointment slots.
        """
        doctor_id = self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        available_slots = self.db_handler.get_available_appointments(doctor_id=doctor_id, date=date)
        self.assertGreater(len(available_slots), 0, "Available slots should be greater than 0.")

    def test_reschedule_appointment(self):
        """
        Test rescheduling an appointment.
        """
        patient_id = self.db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
        self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        appointment_date = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
        new_appointment_date = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        appointment_result = self.db_handler.book_appointment(
            patient_id=patient_id,
            doctor_name="Dr. Smith",
            specialization="Cardiology",
            appointment_date=appointment_date
        )
        appointment_id = appointment_result.split("ID ")[1].split(" ")[0]  # Extract appointment ID
        
        result = self.db_handler.reschedule_appointment(
            appointment_id=appointment_id,
            new_appointment_date=new_appointment_date
        )
        self.assertIn("successfully rescheduled", result)

    def test_cancel_appointment(self):
        """
        Test canceling an appointment.
        """
        patient_id = self.db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
        self.db_handler.add_doctor(name="Dr. Smith", specialization="Cardiology")
        appointment_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        appointment_result = self.db_handler.book_appointment(
            patient_id=patient_id,
            doctor_name="Dr. Smith",
            specialization="Cardiology",
            appointment_date=appointment_date
        )
        appointment_id = appointment_result.split("ID ")[1].split(" ")[0]  # Extract appointment ID
        cancel_result = self.db_handler.cancel_appointment(appointment_id)
        self.assertIn("successfully canceled", cancel_result)

    def test_get_patient_by_contact(self):
        """
        Test retrieving patient details by contact number.
        """
        self.db_handler.add_patient(name="John Doe", age=30, contact=1234567890)
        patient = self.db_handler.get_patient_by_contact(contact=1234567890)
        self.assertIsNotNone(patient, "Patient should not be None.")
        self.assertEqual(patient[1], "John Doe", "Patient name should match.")

if __name__ == "__main__":
    unittest.main()