let carIdToDelete = null;

function confirmDelete(carId) {
    carIdToDelete = carId;
    document.getElementById("confirmModal").style.display = "flex";
}

document.getElementById("cancelBtn").onclick = function() {
    document.getElementById("confirmModal").style.display = "none";
}

document.getElementById("confirmBtn").onclick = function() {
    if (carIdToDelete !== null) {
        fetch(`/delete_car/${carIdToDelete}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams()
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                alert('Eroare la ștergere. Încearcă din nou.');
            }
        })
        .catch(() => {
            alert('A apărut o problemă. Încearcă mai târziu.');
        });
    }
}

function editCar(carId) {
    window.location.href = "/edit_car/" + carId;
}

function confirmLogout() {
    return confirm("Sigur dorești să te deconectezi?");
}

// 🔽 VALIDARE PLĂCUȚĂ AUTO 🔽
const plateInput = document.getElementById('plate');
const errorMessage = document.getElementById('error-message');

if (plateInput) {
    // Lista județelor valide
    const judeteValide = [
        "AB", "AR", "AG", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
        "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ",
        "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT",
        "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"
    ];

    plateInput.addEventListener('input', function () {
        this.value = this.value.toUpperCase().replace(/\s/g, '');

        // Regex pentru placa de înmatriculare
        const regex = /^([A-Z]{1,2})([0-9]{2,3})([A-Z]{3})$/;
        const match = this.value.match(regex);

        if (!match || !judeteValide.includes(match[1])) {
            errorMessage.textContent = "Format invalid. Exemplu: B123XYZ sau CJ12ABC. Verifică județul.";
        } else {
            errorMessage.textContent = "";
        }
    });

    document.getElementById('carForm').addEventListener('submit', function (event) {
        const value = plateInput.value;
        const regex = /^([A-Z]{1,2})([0-9]{2,3})([A-Z]{3})$/;
        const match = value.match(regex);

        if (!match || !judeteValide.includes(match[1])) {
            event.preventDefault();
            errorMessage.textContent = "Format invalid. Nu s-a trimis. Verifică județul.";
        }
    });
}
