const searchBox = document.getElementById("searchBox");
const results = document.getElementById("results");

const confirmationCard = document.getElementById("confirmationCard");
const confirmName = document.getElementById("confirmName");
const confirmOrganization = document.getElementById("confirmOrganization");

const backButton = document.getElementById("backButton");
const continueButton = document.getElementById("continueButton");

const signatureScreen = document.getElementById("signatureScreen");
const signatureName = document.getElementById("signatureName");
const signatureOrganization = document.getElementById("signatureOrganization");

const signatureBackButton = document.getElementById("signatureBackButton");
const submitButton = document.getElementById("submitButton");
const clearSignatureButton =
    document.getElementById("clearSignatureButton");

const title = document.querySelector("h2");
const subtitle = document.querySelector(".subtitle");
const searchBoxContainer = document.querySelector(".search-box");
const toggleRegistration =
    document.getElementById("toggleRegistration");
const divider = document.getElementById("divider");

const canvas = document.getElementById("signaturePad");
const signaturePad = new SignaturePad(canvas);

const successScreen = document.getElementById("successScreen");
const successName = document.getElementById("successName");

let selectedParticipant = null;

searchBox.focus();

/* ==========================================
   Live Search
========================================== */

searchBox.addEventListener("input", async function () {

    const query = this.value.trim();

    if (query.length < 2) {

        results.innerHTML = "";

        results.classList.remove("hidden");
        confirmationCard.classList.add("hidden");
        signatureScreen.classList.add("hidden");

        return;
    }

    try {

        const response = await fetch(
            `/api/search?q=${encodeURIComponent(query)}`
        );

        const matches = await response.json();

        results.innerHTML = "";

        results.classList.remove("hidden");
        confirmationCard.classList.add("hidden");
        signatureScreen.classList.add("hidden");

        if (matches.length === 0) {

            results.innerHTML =
                "<div class='no-results'>No matching registrations found.</div>";

            return;

        }

        matches.forEach(person => {

            const card = document.createElement("div");

            card.className = "result";

            card.innerHTML = `
                <strong>${person.first_name} ${person.last_name}</strong>
                <div class="org">${person.organization}</div>
            `;

            card.onclick = () => {

                selectedParticipant = person;

                confirmName.textContent =
                    `${person.first_name} ${person.last_name}`;

                confirmOrganization.textContent =
                    person.organization;

                results.classList.add("hidden");
                confirmationCard.classList.remove("hidden");

            };

            results.appendChild(card);

        });

    } catch (error) {

    console.error("Check-in error:", error);

    submitButton.disabled = false;

    alert(error.message);


    }

});

/* ==========================================
   Confirmation Screen
========================================== */

backButton.onclick = () => {

    confirmationCard.classList.add("hidden");
    results.classList.remove("hidden");

    selectedParticipant = null;

    searchBox.focus();

};

continueButton.onclick = () => {

    if (!selectedParticipant) return;

    confirmationCard.classList.add("hidden");

    signatureName.textContent =
        `${selectedParticipant.first_name} ${selectedParticipant.last_name}`;

    signatureOrganization.textContent =
        selectedParticipant.organization;

    // Hide search interface
    title.classList.add("hidden");
    subtitle.classList.add("hidden");
    searchBoxContainer.classList.add("hidden");
    results.classList.add("hidden");
    divider.classList.add("hidden");
    toggleRegistration.classList.add("hidden");

    signatureScreen.classList.remove("hidden");

    // Resize AFTER the canvas becomes visible
    setTimeout(() => {
        resizeCanvas();
    }, 0);

};

/* ==========================================
   Signature Screen
========================================== */

signatureBackButton.onclick = () => {

    signatureScreen.classList.add("hidden");

    confirmationCard.classList.remove("hidden");

    // Restore search interface
    title.classList.remove("hidden");
    subtitle.classList.remove("hidden");
    searchBoxContainer.classList.remove("hidden");
    divider.classList.remove("hidden");
    toggleRegistration.classList.remove("hidden");

};

submitButton.onclick = async () => {

    if (signaturePad.isEmpty()) {

        alert("Please sign before checking in.");
        return;

    }

    submitButton.disabled = true;

    const signature = signaturePad.toDataURL("image/png");

    try {

        const response = await fetch("/api/checkin", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                participant: selectedParticipant,
                signature: signature
            })
        });

        if (!response.ok) {

            const text = await response.text();

            console.error(text);

            throw new Error(`Server returned ${response.status}`);

        }

        // Hide signature screen
        signatureScreen.classList.add("hidden");

        // Show success screen
        successName.textContent =
            `${selectedParticipant.first_name} ${selectedParticipant.last_name}`;

        successScreen.classList.remove("hidden");

        // Reset after 3 seconds
        setTimeout(() => {

            successScreen.classList.add("hidden");

            title.classList.remove("hidden");
            subtitle.classList.remove("hidden");
            searchBoxContainer.classList.remove("hidden");
            divider.classList.remove("hidden");
            toggleRegistration.classList.remove("hidden");

            confirmationCard.classList.add("hidden");
            results.classList.remove("hidden");

            searchBox.value = "";
            results.innerHTML = "";

            selectedParticipant = null;

            signaturePad.clear();

            submitButton.disabled = false;

            searchBox.focus();

        }, 3000);

    } catch (error) {

        console.error(error);

        submitButton.disabled = false;

        alert("Unable to save check-in.");

    }

};

clearSignatureButton.onclick = () => {

    signaturePad.clear();

};

function resizeCanvas() {

    const ratio = Math.max(window.devicePixelRatio || 1, 1);

    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;

    canvas.getContext("2d").scale(ratio, ratio);

    signaturePad.clear();

}

window.addEventListener("resize", resizeCanvas);