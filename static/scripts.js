function startStream() {
    const outputElement = document.getElementById('output');
    outputElement.innerHTML = ''; // Clear previous output

    const eventSource = new EventSource('/agent');
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const formattedText = formatResponse(data);
        outputElement.innerHTML += `<p>${formattedText}</p>`;
    };

    eventSource.onerror = function() {
        outputElement.innerHTML += '<p><strong>Error:</strong> Unable to stream data.</p>';
        eventSource.close();
    };
}

//format agent stream response
function formatResponse(data) {
    // Check if the data contains text
    if (data.text) {
        // Replace newlines with HTML line breaks and wrap in a paragraph
        return `<p>${data.text.replace(/\n/g, '<br/>')}</p>`;
    }
    // Fallback to JSON string with additional formatting
    return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
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
