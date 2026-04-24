const stationSelect = document.getElementById("station");
const destinationInput = document.getElementById("destination");
const resultDiv = document.getElementById("result");

async function findRoute() {
    const station = stationSelect.value.trim();
    const destination = destinationInput.value.trim();

    if (!station || !destination) {
        alert("Please select station and enter destination");
        return;
    }

    resultDiv.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch("http://127.0.0.1:5001/get_places", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ station, destination })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        displayResult(data);
    } catch (error) {
        console.error("Error:", error);
        resultDiv.innerHTML = `<p>${error.message || "Failed to fetch data. Check backend."}</p>`;
    }
}

function displayResult(data) {
    if (!data || data.error) {
        resultDiv.innerHTML = `<p>${data?.error || "No data found"}</p>`;
        return;
    }

    resultDiv.innerHTML = `
        <h3>Station: ${data.station || "N/A"}</h3>
        <p>Destination: ${data.destination || "N/A"}</p>
        <p>Nearest Exit: ${data.exit || "N/A"}</p>
        <p>Distance: ${data.distance || "N/A"}</p>
        <p>Walking Time: ${data.walking_time || "N/A"}</p>
        <p>Waiting Time: ${data.waiting_time || "N/A"}</p>
        <p>Vehicle Time: ${data.vehicle_time || "N/A"}</p>
        <h4>Suggestion: ${data.suggestion || "No suggestion"}</h4>
    `;
}

document.getElementById("searchBtn")?.addEventListener("click", findRoute);
