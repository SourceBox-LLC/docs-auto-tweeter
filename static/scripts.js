function startStream() {
    const form = document.querySelector('form');
    const formData = new FormData(form);
    let prompt = formData.get('prompt');

    const customPromptArea = document.getElementById('customPromptArea');
    const customPromptText = document.getElementById('customPromptText').value.trim();

    // Use custom prompt if it's visible and not empty
    if (customPromptArea.style.display === 'block' && customPromptText) {
        prompt = customPromptText;
    }

    // Send the prompt using fetch
    fetch('/agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ prompt: prompt })
    }).then(response => {
        if (response.ok) {
            // Start the EventSource stream
            const eventSource = new EventSource('/agent');
            eventSource.onmessage = function(event) {
                const output = document.getElementById('output');
                output.innerHTML += event.data + "<br>";
            };
        } else {
            console.error('Failed to send prompt');
        }
    }).catch(error => console.error('Error:', error));
}

function toggleCustomPrompt() {
    const customPromptArea = document.getElementById('customPromptArea');
    customPromptArea.style.display = customPromptArea.style.display === 'none' ? 'block' : 'none';
}

function selectRandomPrompt() {
    const selectElement = document.querySelector('select[name="prompt"]');
    const options = selectElement.options;
    const randomIndex = Math.floor(Math.random() * options.length);
    selectElement.selectedIndex = randomIndex;
}

document.addEventListener('DOMContentLoaded', function() {
    const customPromptText = document.getElementById('customPromptText');
    customPromptText.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevents adding a new line
            startStream(); // Submits the prompt
        }
    });
});