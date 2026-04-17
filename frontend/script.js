async function getRecommendation() {
    const station = document.getElementById("station").value;
    const destination = document.getElementById("destination").value;

    const response = await fetch(
        `http://127.0.0.1:5000/recommend?station=${station}&destination=${destination}`
    );

    const data = await response.json();

    document.getElementById("result").innerHTML = `
        <p>🚶 Walking Time: ${data.walking_time} mins</p>
        <p>⏳ Waiting Time: ${data.waiting_time} mins</p>
        <h3>✅ Suggestion: ${data.suggestion}</h3>
    `;
}