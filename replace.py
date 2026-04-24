import sys

with open('frontend/connector.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    <!-- Destination -->
    <input type="text" id="destination" placeholder="Enter Destination">

    <button onclick="nextPage()">Get Details</button>

</div>

<script>

// Get selected line from welcome.html"""

replacement = """    <!-- Destination -->
    <div style="display: flex; align-items: center; margin-top: 12px; gap: 10px;">
        <input type="text" id="destination" placeholder="Enter Destination" style="margin-top: 0; flex: 1;">
        <button id="mic-btn" onclick="startDictation()" style="margin-top: 0; width: 50px; background: #eab308; font-size: 20px; padding: 5px; border-radius: 8px; border: 1px solid #ccc; cursor: pointer;" title="Speak Destination">🎤</button>
    </div>

    <button onclick="nextPage()" style="margin-top: 15px;">Get Details</button>

</div>

<script>
// Voice Dictation setup
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-IN";
        
        const micBtn = document.getElementById('mic-btn');
        micBtn.style.background = "#ef4444"; // red while listening

        recognition.start();

        recognition.onresult = function(e) {
            document.getElementById('destination').value = e.results[0][0].transcript;
            recognition.stop();
            micBtn.style.background = "#eab308";
        };

        recognition.onerror = function(e) {
            recognition.stop();
            micBtn.style.background = "#eab308";
        };
    } else {
        alert("Your browser does not support Voice Input.");
    }
}

// Get selected line from welcome.html"""

if target in content:
    with open('frontend/connector.html', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Replaced")
else:
    print("Target not found. Please check CRLF vs LF.")
    target_crlf = target.replace('\n', '\r\n')
    if target_crlf in content:
        with open('frontend/connector.html', 'w', encoding='utf-8') as f:
            f.write(content.replace(target_crlf, replacement))
        print("Replaced CRLF")
    else:
        print("Still not found")
