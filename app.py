import os
from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    jsonify,
)

from services.jotform import get_registrations

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


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(debug=True)
