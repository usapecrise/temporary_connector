import os
from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)

from services.airtable import (
    get_active_events,
    get_workshop,
    create_attendance,
    upload_signature,
)

from services.jotform import get_registrations

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

CONNECTOR_TOKEN = os.getenv("CONNECTOR_TOKEN")

print("Connector token loaded:", bool(CONNECTOR_TOKEN))

if not CONNECTOR_TOKEN:
    raise RuntimeError(
        "CONNECTOR_TOKEN environment variable is not set."
    )


# ---------------------------------------------------------
# Existing kiosk registration cache
# ---------------------------------------------------------

registration_cache = {}


# ---------------------------------------------------------
# EXISTING KIOSK APP
# ---------------------------------------------------------

@app.route("/")
def select_event():
    events = get_active_events()
    return render_template(
        "select.html",
        events=events
    )


@app.route("/start", methods=["POST"])
def start():
    record_id = request.form["event"]

    workshop = get_workshop(record_id)

    registrations = get_registrations(
        workshop["registration_form_id"]
    )

    registration_cache[record_id] = registrations
    session["workshop_id"] = record_id

    return redirect(url_for("search"))


@app.route("/search")
def search():
    if "workshop_id" not in session:
        return redirect(url_for("select_event"))

    return render_template("search.html")


@app.route("/api/search")
def api_search():
    if "workshop_id" not in session:
        return jsonify([])

    workshop_id = session["workshop_id"]

    registrations = registration_cache.get(
        workshop_id,
        []
    )

    query = request.args.get(
        "q",
        ""
    ).strip().lower()

    if not query:
        return jsonify([])

    matches = []

    for person in registrations:

        first_name = person.get(
            "first_name",
            ""
        )

        last_name = person.get(
            "last_name",
            ""
        )

        email = person.get(
            "email",
            ""
        )

        full_name = (
            f"{first_name} {last_name}"
        ).strip().lower()

        if (
            query in full_name
            or query in email.lower()
        ):
            matches.append(person)

    return jsonify(matches)


@app.route(
    "/api/checkin",
    methods=["POST"]
)
def checkin():

    data = request.get_json()

    participant = data["participant"]
    signature = data["signature"]

    workshop_id = session.get(
        "workshop_id"
    )

    if not workshop_id:
        return jsonify({
            "success": False,
            "error": "No workshop selected"
        }), 400

    workshop = get_workshop(
        workshop_id
    )

    record = {
        **participant,
        **workshop
    }

    attendance_id = create_attendance(
        record
    )

    upload_signature(
        attendance_id,
        signature,
        participant
    )

    return jsonify({
        "success": True
    })


# ---------------------------------------------------------
# REUSABLE JOTFORM REMOTE DATA DROPDOWN
# ---------------------------------------------------------

@app.route("/api/registrants")
def api_registrants():

    # Registration form ID is supplied by
    # the sign-in form's dropdown URL.
    #
    # Example:
    #
    # /api/registrants?form_id=262514782185967

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

    print("Header present:", bool(auth_header))
    print("Header length:", len(auth_header))
    print("Token length:", len(CONNECTOR_TOKEN))
    print("Tokens match:", auth_header == CONNECTOR_TOKEN)

    if auth_header != CONNECTOR_TOKEN:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    # Basic validation:
    # Jotform form IDs should only contain digits.
    if not form_id.isdigit():
        return jsonify({
            "error": "Invalid form_id"
        }), 400

    try:

        registrations = get_registrations(
            form_id
        )

        # Jotform Remote Data Dropdown
        # will add:
        #
        # &search=Jessica
        #
        # when the participant types.
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

            # What participant sees in dropdown
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

            # Fields participant may search
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

        # Limit dropdown results
        return jsonify(
            results[:50]
        )

    except Exception as e:

        print(
            "Error loading registrants:",
            repr(e)
        )

        return jsonify({
            "error":
                "Unable to load registrants"
        }), 500


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


# ---------------------------------------------------------
# START APP
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )