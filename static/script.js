// Initialize speech recognition
let recognition;

function startRecognition() {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        alert("Tarayıcınız konuşma tanımayı desteklemiyor.");
        return;
    }

    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'tr-TR';  // Set language to Turkish
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        // Capture the recognized speech and insert it into the text area
        const transcript = event.results[0][0].transcript;
        document.getElementById('user_input').value = transcript;
        console.log("Recognized text: " + transcript); // Log recognized text
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
        alert("Hata oluştu: " + event.error); // Alert the error to the user
    };

    recognition.onstart = function() {
        console.log("Speech recognition started");
    };

    recognition.onaudioend = function() {
        console.log("Speech recognition ended");
    };

    try {
        recognition.start();
    } catch (error) {
        console.error("Speech recognition could not start: ", error);
    }
}
