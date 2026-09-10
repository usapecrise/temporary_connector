/* =====================================================
   WORKSHOP CHECK-IN KIOSK
   Part 1
===================================================== */

let selectedParticipant = null;
let signaturePad = null;

/* =====================================================
   SCREENS
===================================================== */

const searchScreen = document.getElementById("searchScreen");
const previewScreen = document.getElementById("previewScreen");
const confirmScreen = document.getElementById("confirmScreen");
const loadingScreen = document.getElementById("loadingScreen");
const successScreen = document.getElementById("successScreen");

/* =====================================================
   SEARCH
===================================================== */

const searchBox = document.getElementById("searchBox");
const results = document.getElementById("results");

/* =====================================================
   PREVIEW
===================================================== */
const previewName = document.getElementById("previewName");
const previewOrganization = document.getElementById("previewOrganization");
const previewEconomy = document.getElementById("previewEconomy");

/* =====================================================
   SIGNATURE SCREEN
===================================================== */

const signatureName =
    document.getElementById("signatureName");

const canvas =
    document.getElementById("signaturePad");

/* =====================================================
   BUTTONS
===================================================== */

const confirmButton =
    document.getElementById("confirmButton");

const changeButton =
    document.getElementById("changeButton");

const submitAttendance =
    document.getElementById("submitAttendance");

const signatureResetButton =
    document.getElementById("signatureResetButton");

const clearSignatureButton =
    document.getElementById("clearSignatureButton");

const registerButton =
    document.getElementById("registerButton");

/* =====================================================
   SEARCH
===================================================== */

searchBox.addEventListener("input", function () {

    const search =
        this.value
            .trim()
            .toLowerCase();

    if (search.length < 2) {

        showResults([]);

        return;

    }

    fetch(`/api/search?q=${encodeURIComponent(search)}`)
    .then(response => response.json())
    .then(matches => {
        showResults(matches);
    });

});

/* =====================================================
   SHOW SEARCH RESULTS
===================================================== */

function showResults(list) {

    results.innerHTML = "";

    if (list.length === 0) {

        results.innerHTML = `
            <div class="no-results">
                No matching registrations found.
            </div>
        `;

        return;

    }

    list
        .slice(0, 8)
        .forEach(person => {

            const div =
                document.createElement("div");

            div.className = "result";

            div.innerHTML = `
                <strong>${`${person.first_name} ${person.last_name}`.trim()}</strong>
                <div class="org">
                    ${person.organization}
                    •
                    ${person.economy}
                </div>
            `;

            div.onclick = () => {

                selectedParticipant = person;

                showPreview();

            };

            results.appendChild(div);

        });

}

/* =====================================================
   PREVIEW SCREEN
===================================================== */

function showPreview() {

    previewName.textContent =
        `${selectedParticipant.first_name} ${selectedParticipant.last_name}`;

    previewOrganization.textContent =
        selectedParticipant.organization;

    previewEconomy.textContent =
        selectedParticipant.economy;

    signatureName.textContent =
        `${selectedParticipant.first_name} ${selectedParticipant.last_name}`;

    searchScreen.classList.add("hidden");

    previewScreen.classList.remove("hidden");

}

/* =====================================================
   SCREEN HELPERS
===================================================== */

function showLoading() {

    previewScreen.classList.add("hidden");

    confirmScreen.classList.add("hidden");

    loadingScreen.classList.remove("hidden");

}

function showSuccess() {

    loadingScreen.classList.add("hidden");

    successScreen.classList.remove("hidden");

    setTimeout(resetKiosk, 4000);

}

/* =====================================================
   BUTTON EVENTS
===================================================== */

confirmButton.onclick = () => {

    previewScreen.classList.add("hidden");

    confirmScreen.classList.remove("hidden");

    setTimeout(() => {

        initializeSignaturePad();

    }, 50);

};

changeButton.onclick = resetKiosk;

signatureResetButton.onclick = () => {

    confirmScreen.classList.add("hidden");

    previewScreen.classList.remove("hidden");

    clearSignature();

};

clearSignatureButton.onclick = () => {

    clearSignature();

};

registerButton.onclick = () => {

    window.open(
        "YOUR_JOTFORM_URL",
        "_blank"
    );

};

/* =====================================================
   SIGNATURE PAD
===================================================== */

function initializeSignaturePad() {

    const ratio = Math.max(window.devicePixelRatio || 1, 1);

    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = 250 * ratio;

    canvas.getContext("2d").scale(ratio, ratio);

    signaturePad = new SignaturePad(canvas, {
        backgroundColor: "rgb(255,255,255)",
        penColor: "rgb(25,25,25)"
    });

}

function clearSignature() {

    if (signaturePad) {

        signaturePad.clear();

    }

}

/* =====================================================
   SUBMIT ATTENDANCE
===================================================== */

submitAttendance.onclick = () => {

    if (!selectedParticipant) {

        alert("No participant selected.");

        return;

    }

    if (!signaturePad || signaturePad.isEmpty()) {

        alert("Please provide your signature.");

        return;

    }

    const signatureImage =
        signaturePad.toDataURL("image/png");

    console.log("Participant:");

    console.log(selectedParticipant);

    console.log("Signature:");

    console.log(signatureImage);

    showLoading();

    /*
    ======================================================

    NEXT STEP

    Replace this simulated delay with:

    1. Duplicate attendance check
    2. Populate hidden Jotform fields
    3. Submit Jotform
    4. Wait for success
    5. showSuccess()

    ======================================================
    */

    setTimeout(() => {

        showSuccess();

    }, 1500);

};

/* =====================================================
   RESET
===================================================== */

function resetKiosk() {

    selectedParticipant = null;

    searchBox.value = "";

    results.innerHTML = "";

    searchScreen.classList.remove("hidden");

    previewScreen.classList.add("hidden");

    confirmScreen.classList.add("hidden");

    loadingScreen.classList.add("hidden");

    successScreen.classList.add("hidden");

    clearSignature();

    searchBox.focus();

}

/* =====================================================
   HELPERS
===================================================== */

function getInitials(name) {

    if (!name) {

        return "";

    }

    return name
        .trim()
        .split(/\s+/)
        .map(word => word.charAt(0))
        .join("")
        .substring(0, 2)
        .toUpperCase();

}

/* =====================================================
   RESIZE SIGNATURE PAD
===================================================== */

window.addEventListener("resize", () => {

    if (!confirmScreen.classList.contains("hidden")) {

        initializeSignaturePad();

    }

});

/* =====================================================
   OPTIONAL KEYBOARD SHORTCUTS
===================================================== */

document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {

        resetKiosk();

    }

});

/* =====================================================
   STARTUP
===================================================== */

resetKiosk();

console.log("Workshop Check-In kiosk ready.");