"""
airtable.py

All Airtable communication for the
US APEC-RISE Check-In application.
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

if not AIRTABLE_API_KEY:
    raise RuntimeError("AIRTABLE_API_KEY is not configured.")

if not AIRTABLE_BASE_ID:
    raise RuntimeError("AIRTABLE_BASE_ID is not configured.")

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

WORKSHOP_TABLE = "Workshop Reference List"

ATTENDANCE_TABLES = {
    "Workshop": "OT1 Sign-Ins (Workshops)",
    "Dialogue": "Other Sign-Ins (Meetings_Dialogues)"
}



# ------------------------------------------------------
# Helpers
# ------------------------------------------------------

def airtable_url(table):
    return f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}"


# ------------------------------------------------------
# Active Events
# ------------------------------------------------------

def get_active_events():
    """
    Returns all events where
    Check-In Enabled = TRUE().
    """

    response = requests.get(
        airtable_url(WORKSHOP_TABLE),
        headers=HEADERS,
        params={
            "filterByFormula": "{Check-In Enabled}=TRUE()"
        },
        timeout=30
    )

    response.raise_for_status()

    events = []

    for record in response.json().get("records", []):

        fields = record.get("fields", {})

        events.append({

            "record_id": record["id"],

            "workshop":
                fields.get("Workshop", ""),

            "activity_type":
                fields.get("Activity Type", ""),

            "registration_form_id":
                fields.get("Registration Form ID", ""),

            "start_date":
                fields.get("Start Date", ""),

            "end_date":
                fields.get("End Date", ""),

            "city":
                fields.get("City", ""),

            "economy":
                fields.get("Economy", ""),

            "workstream":
                fields.get("Workstream", ""),

            "indicator":
                fields.get("Indicator ID", ""),

            "fiscal_year":
                fields.get("Fiscal Year", "")

        })

    return events


# ------------------------------------------------------
# Single Event
# ------------------------------------------------------

def get_workshop(record_id):
    """
    Return one workshop configuration.
    """

    response = requests.get(
        airtable_url(WORKSHOP_TABLE),
        headers=HEADERS,
        params={
            "filterByFormula": f"RECORD_ID()='{record_id}'"
        },
        timeout=30
    )

    response.raise_for_status()

    records = response.json().get("records", [])

    if not records:
        raise ValueError(f"Workshop not found: {record_id}")

    fields = records[0]["fields"]

    workshop = {

        "record_id": record_id,

        "workshop":
            fields.get("Workshop", ""),

        "activity_type":
            fields.get("Activity Type", ""),

        "registration_form_id":
            fields.get("Registration Form ID", ""),

        "start_date":
            fields.get("Start Date", ""),

        "end_date":
            fields.get("End Date", ""),

        "city":
            fields.get("City", ""),

        "economy":
            fields.get("Economy", ""),

        "workstream":
            fields.get("Workstream", ""),

        "indicator":
            fields.get("Indicator ID", ""),

        "fiscal_year":
            fields.get("Fiscal Year", "")

    }

    return workshop


# ------------------------------------------------------
# Attendance
# ------------------------------------------------------

def create_attendance(record):
    """
    Create one attendance record.
    """

    activity_type = record["activity_type"]

    table = ATTENDANCE_TABLES.get(activity_type)

    if not table:
        raise ValueError(
            f"Unknown activity type: {activity_type}"
        )

    fields = {

        "First Name":
            record.get("first_name", ""),

        "Last Name":
            record.get("last_name", ""),

        "Email Address":
            record.get("email", ""),

        "Organization":
            record.get("organization", ""),

        "Economy":
            record.get("economy", ""),

        "Job Position / Title":
            record.get("job_title", ""),

        "Workshop":
            record.get("workshop", ""),

        "Workshop Date":
            record.get("start_date", ""),

        "Workstream":
            record.get("workstream", ""),

        "Indicator ID":
            record.get("indicator", ""),

        "City":
            record.get("city", ""),

        "Fiscal Year":
            record.get("fiscal_year", ""),

        "Notes":
            record.get("notes", "")

    }

    response = requests.post(
        airtable_url(table),
        headers=HEADERS,
        json={
            "fields": fields
        },
        timeout=30
    )

    response.raise_for_status()

    created = response.json()

    return created["id"]


# ------------------------------------------------------
# Signature
# ------------------------------------------------------
#
#  
def upload_signature(
    record_id,
    signature,
    participant
):
    """
    Upload a signature directly to the
    Signature attachment field.
    """

    if "," not in signature:
        raise ValueError("Invalid signature.")

    encoded = signature.split(",", 1)[1]

    filename = (
        f"{participant.get('first_name','Participant')}-"
        f"{participant.get('last_name','')}-"
        f"{datetime.now():%Y%m%d-%H%M%S}.png"
    )

    response = requests.post(
        (
            f"https://content.airtable.com/v0/"
            f"{AIRTABLE_BASE_ID}/"
            f"{record_id}/"
            f"Signature/"
            f"uploadAttachment"
        ),
        headers=HEADERS,
        json={
            "contentType": "image/png",
            "file": encoded,
            "filename": filename
        },
        timeout=60
    )

    from pprint import pprint

    response.raise_for_status()
    return response.json()