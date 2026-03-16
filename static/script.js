const form = document.getElementById("calendarForm");
const button = document.getElementById("generateBtn");
const loadingBox = document.getElementById("loadingBox");

if (form) {
    form.addEventListener("submit", function () {
        button.disabled = true;
        button.textContent = "Generating...";
        loadingBox.classList.remove("hidden");
    });
}