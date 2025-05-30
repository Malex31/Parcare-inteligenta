document.getElementById("verifyForm").addEventListener("submit", function (e) {
    const code = document.querySelector('input[name="code"]').value.trim();
    const errorMessage = document.getElementById("errorMessage");

    if (!code) {
        e.preventDefault();
        errorMessage.textContent = "Te rugăm să introduci codul primit.";
        errorMessage.style.display = "block";
    } else {
        errorMessage.style.display = "none";
    }
});
