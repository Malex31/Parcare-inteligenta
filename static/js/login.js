document.getElementById("authForm").addEventListener("submit", function (e) {
    const email = document.querySelector('input[name="email"]').value.trim();
    const password = document.querySelector('input[name="password"]').value.trim();
    const errorMessage = document.getElementById("errorMessage");

    if (!email || !password) {
        e.preventDefault();
        errorMessage.textContent = "Te rugăm să completezi toate câmpurile.";
        errorMessage.style.display = "block";
    } else {
        errorMessage.style.display = "none";
    }
});
