// Get elements
const stationSelect = document.getElementById("station");
const destinationInput = document.getElementById("destination");
const resultDiv = document.getElementById("result");

// Function to fetch data from backend
async function findRoute() {
    const station = stationSelect.value.trim();
    const destination = destinationInput.value.trim();

    // Validation
    if (!station || !destination) {
        alert("Please select station and enter destination");
        return;
    }

    // Show loading
    resultDiv.innerHTML = "<p>⏳ Loading...</p>";

    try {
        const response = await fetch("http://127.0.0.1:5000/get_places", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                station: station,
                destination: destination
            })
        });

        // Check response status
        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        console.log("API Response:", data); // Debug

        displayResult(data);

    } catch (error) {
        console.error("Error:", error);
        resultDiv.innerHTML = "<p>❌ Failed to fetch data. Check backend.</p>";
    }
}

// Function to display result
function displayResult(data) {
    if (!data || Object.keys(data).length === 0) {
        resultDiv.innerHTML = "<p>No data found</p>";
        return;
    }

    // Nearby places rendering fix
    let placesHTML = "";

    if (Array.isArray(data.places) && data.places.length > 0) {
        placesHTML = data.places
            .map(place => <li>🏬 ${place}</li>)
            .join("");
    } else {
        placesHTML = "<li>No nearby places found</li>";
    }

    // Display result
    resultDiv.innerHTML = `
        <h3>🚇 Line: ${data.line || "N/A"}</h3>
        <p>📍 Station: ${data.station || "N/A"}</p>
        <p>🎯 Destination: ${data.destination || "N/A"}</p>

        <h4>🚕 Auto Availability: ${data.auto || "Not available"}</h4>
        <h4>🚌 Bus Timing: ${data.bus || "Not available"}</h4>

        <h4>🚶 Walking Time: ${data.bus_walking_time || "Not available"}</h4>
        <h4>💡 Suggestion: ${data.suggestion || "No suggestion"}</h4>

        <h4>🛍️ Nearby Places:</h4>
        <ul>${placesHTML}</ul>
    `;
}

// Button click event
document.getElementById("searchBtn").addEventListener("click", findRoute);