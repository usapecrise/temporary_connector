import os
from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    jsonify,
)

from services.jotform import (
    get_registrations,
    update_submission,
)

load_dotenv()

app = Flask(__name__)

CONNECTOR_TOKEN = os.getenv("CONNECTOR_TOKEN")

if not CONNECTOR_TOKEN:
    raise RuntimeError(
        "CONNECTOR_TOKEN environment variable is not set."
    )


@app.route("/api/registrants")
def api_registrants():

    form_id = request.args.get(
        "form_id",
        ""
    ).strip()

    if not form_id:
        return jsonify({
            "error": "Missing form_id"
        }), 400

    auth_header = request.headers.get(
        "Authorization",
        ""
    ).strip()
    
    if auth_header.lower().startswith("bearer "):
        auth_header = auth_header[7:].strip()
    
    if auth_header != CONNECTOR_TOKEN:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    if not form_id.isdigit():
        return jsonify({
            "error": "Invalid form_id"
        }), 400

    try:

        registrations = get_registrations(
            form_id
        )

        query = request.args.get(
            "search",
            ""
        ).strip().lower()

        results = []

        for person in registrations:

            first_name = person.get(
                "first_name",
                ""
            )

            last_name = person.get(
                "last_name",
                ""
            )

            organization = person.get(
                "organization",
                ""
            )

            economy = person.get(
                "economy",
                ""
            )

            email = person.get(
                "email",
                ""
            )

            submission_id = person.get(
                "submission_id",
                ""
            )

            full_name = (
                f"{first_name} {last_name}"
            ).strip()

            label_parts = [
                full_name,
                organization,
                economy,
            ]

            label = " — ".join(
                str(part).strip()
                for part in label_parts
                if str(part).strip()
            )

            searchable_text = " ".join([
                full_name,
                str(organization),
                str(economy),
                str(email),
            ]).lower()

            if (
                query
                and query not in searchable_text
            ):
                continue

            results.append({
                "id": submission_id,
                "label": label,
                "first_name": first_name,
                "last_name": last_name,
                "organization": organization,
                "economy": economy,
            })

        results.sort(
            key=lambda x:
            x["label"].lower()
        )

        return jsonify(
            results[:50]
        )

    except Exception as e:

        print(
            "Error loading registrants:",
            repr(e)
        )

        return jsonify({
            "error": "Unable to load registrants"
        }), 500
@app.route("/api/registrant")
def api_registrant():

    submission_id = request.args.get(
        "id",
        ""
    ).strip()

    form_id = request.args.get(
        "form_id",
        ""
    ).strip()

    if not submission_id or not form_id:
        return jsonify({
            "error": "Missing id or form_id"
        }), 400

    auth_header = request.headers.get(
        "Authorization",
        ""
    ).strip()

    if auth_header.lower().startswith("bearer "):
        auth_header = auth_header[7:].strip()

    if auth_header != CONNECTOR_TOKEN:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    try:
        registrations = get_registrations(form_id)

        for person in registrations:
            if str(person.get("submission_id", "")) == submission_id:
                return jsonify(person)

        return jsonify({
            "error": "Registrant not found"
        }), 404

    except Exception as e:
        print("Error loading registrant:", repr(e))

        return jsonify({
            "error": "Unable to load registrant"
        }), 500

@app.route("/webhook/signin", methods=["POST"])
def webhook_signin():

    token = request.args.get(
        "token",
        ""
    ).strip()

    if token != CONNECTOR_TOKEN:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    try:
        import json

        # Jotform sends the submitted fields inside rawRequest
        raw_request = request.form.get(
            "rawRequest",
            "{}"
        )

        data = json.loads(raw_request)

        # This is the NEW sign-in submission
        signin_submission_id = request.form.get(
            "submissionID",
            ""
        ).strip()

        # q29 is the Remote Data Dropdown.
        # Its saved value is the ORIGINAL registration submission ID.
        registration_id = str(
            data.get(
                "q29_typeA",
                ""
            )
        ).strip()

        # If this person did not select an existing registration,
        # there is nothing for the connector to fill.
        if not registration_id:
            return jsonify({
                "status": "no registration selected"
            }), 200

        # Registration form for this workshop
        registration_form_id = "262514782185967"

        registrations = get_registrations(
            registration_form_id
        )

        registrant = None

        for person in registrations:
            if str(
                person.get(
                    "submission_id",
                    ""
                )
            ) == registration_id:
                registrant = person
                break

        if not registrant:
            return jsonify({
                "error": "Registrant not found"
            }), 404

        # Populate the blank fields in the SIGN-IN submission
        fields = {
            "2": {
                "first": registrant.get(
                    "first_name",
                    ""
                ),
                "last": registrant.get(
                    "last_name",
                    ""
                ),
            },
            "23": registrant.get(
                "sex",
                ""
            ),
            "14": registrant.get(
                "economy",
                ""
            ),
            "15": registrant.get(
                "email",
                ""
            ),
            "19": registrant.get(
                "organization",
                ""
            ),
        }

        update_submission(
            signin_submission_id,
            fields
        )

        print(
            "Updated sign-in submission:",
            signin_submission_id
        )

        print(
            "Using registration:",
            registration_id
        )

        return jsonify({
            "status": "updated"
        }), 200

    except Exception as e:

        print(
            "Webhook error:",
            repr(e)
        )

        return jsonify({
            "error": "Webhook processing failed"
        }), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(debug=True)
