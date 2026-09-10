"""
jotform.py

Read registrations from Jotform Enterprise.
"""

import os
import requests

from dotenv import load_dotenv


load_dotenv()


JOTFORM_API_KEY = os.getenv(
    "JOTFORM_API_KEY"
)


if not JOTFORM_API_KEY:
    raise RuntimeError(
        "JOTFORM_API_KEY environment variable is not set."
    )


HEADERS = {
    "APIKEY": JOTFORM_API_KEY
}


# IMPORTANT:
# Your Enterprise account requires
# the custom-domain API endpoint.
BASE_URL = (
    "https://apec-rise.jotform.com/API"
)


def get_registrations(form_id):

    url = (
        f"{BASE_URL}/form/"
        f"{form_id}/submissions"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        params={
            "limit": 1000
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    submissions = data.get(
        "content",
        []
    )

    participants = []

    for submission in submissions:

        answers = submission.get(
            "answers",
            {}
        )

        person = {
            "submission_id": str(
                submission.get(
                    "id",
                    ""
                )
            ),
            "first_name": "",
            "last_name": "",
            "email": "",
            "organization": "",
            "economy": "",
            "job_title": "",
            "sex": "",
        }

        for answer in answers.values():

            field = answer.get(
                "name",
                ""
            )

            value = answer.get(
                "answer",
                ""
            )

            # -------------------------
            # Full Name
            # -------------------------

            if field == "fullName":

                if isinstance(
                    value,
                    dict
                ):

                    person[
                        "first_name"
                    ] = str(
                        value.get(
                            "first",
                            ""
                        )
                    ).strip()

                    person[
                        "last_name"
                    ] = str(
                        value.get(
                            "last",
                            ""
                        )
                    ).strip()

                elif isinstance(
                    value,
                    str
                ):

                    parts = (
                        value
                        .strip()
                        .split()
                    )

                    if parts:
                        person[
                            "first_name"
                        ] = parts[0]

                    if len(parts) > 1:
                        person[
                            "last_name"
                        ] = " ".join(
                            parts[1:]
                        )

            # -------------------------
            # Email
            # -------------------------

            elif field == "emailAddress":

                person["email"] = str(
                    value or ""
                ).strip()

            # -------------------------
            # Organization
            # -------------------------

            elif field == (
                "organizationaffiliation"
            ):

                person[
                    "organization"
                ] = str(
                    value or ""
                ).strip()

            # -------------------------
            # Economy
            # -------------------------

            elif field == "economy":

                person["economy"] = str(
                    value or ""
                ).strip()


            elif field == "sex":
                person["sex"] = str(
                    value or ""
                ).strip()
                        
            # -------------------------
            # Job Title
            # -------------------------

            elif field == (
                "jobPositiontitle"
            ):

                person[
                    "job_title"
                ] = str(
                    value or ""
                ).strip()

        if (
            person["first_name"]
            or person["last_name"]
        ):
            participants.append(
                person
            )

    return participants
