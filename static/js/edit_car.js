// La input, forțează scrierea cu majuscule și elimină spațiile
document.getElementById("plate").addEventListener("input", function () {
    this.value = this.value.toUpperCase().replace(/\s/g, '');
});

// La submit, validăm formatul complet
document.getElementById("editForm").addEventListener("submit", function (e) {
    const plateInput = document.getElementById("plate");
    const plate = plateInput.value.trim().toUpperCase().replace(/\s/g, '');
    const errorMessage = document.getElementById("errorMessage");

    // Regex pentru placa de înmatriculare:
    // 1 sau 2 litere, 2 sau 3 cifre, 3 litere, toate lipite
    const pattern = /^([A-Z]{1,2})(\d{2,3})([A-Z]{3})$/;

    // Lista județelor valide
    const judeteValide = [
        "AB", "AR", "AG", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
        "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ",
        "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT",
        "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"
    ];

    const match = plate.match(pattern);

    if (!match) {
        e.preventDefault();
        errorMessage.textContent = "Format invalid. Exemplu: B123ABC sau CJ45XYZ";
        errorMessage.style.display = "block";
        return;
    }

    // Verificăm dacă prefixul județului este valid
    if (!judeteValide.includes(match[1])) {
        e.preventDefault();
        errorMessage.textContent = "Județ invalid în numărul de înmatriculare.";
        errorMessage.style.display = "block";
        return;
    }

    // Dacă totul e ok, ascundem mesajul de eroare
    errorMessage.style.display = "none";
    plateInput.value = plate; // forțăm valoarea corectă (majuscule fără spații)
});
