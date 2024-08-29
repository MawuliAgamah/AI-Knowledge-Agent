// Function to log the bounds of the window
function logWindowBounds() {
    const bounds = {
        width: window.innerWidth,
        height: window.innerHeight,
        outerWidth: window.outerWidth,
        outerHeight: window.outerHeight
    };

    console.log("Window bounds:", bounds);

    // Log coordinates of each corner
    console.log(
        "Top-left corner:", { x: 0, y: 0 },
        "Top-right corner:", { x: bounds.width, y: 0 },
        "Bottom-left corner:", { x: 0, y: bounds.height },
        "Bottom-right corner:", { x: bounds.width, y: bounds.height }
    );
}
logWindowBounds();
// Log window bounds on resize
window.addEventListener('resize', logWindowBounds);


// Create the pop up element 
const popup = document.createElement('div');
popup.className = 'chat-popup';

// Design the HTML for the pop up 
popup.innerHTML = `
    <button class="close-popup-button" id="closePopup">×</button>
    <form method="post" id="promptForm"> 
    <input type="text" id="chatInput" placeholder="Chat with AI here...">
    <button type="submit" name="submit-prompt" class="submit-button" id="submitChat">Generate</button>
    </form>
`;
document.body.appendChild(popup);



function getCaretPosition() {
    const selection = window.getSelection();
    if (!selection.rangeCount) return null;

    const range = selection.getRangeAt(0);
    const editor = document.querySelector('.text-editor-element');
    if (!editor.contains(range.commonAncestorContainer)) return null;

    const editorRect = editor.getBoundingClientRect();
    const rangeRect = range.getBoundingClientRect();

    return {
        x: rangeRect.right - editorRect.left,
        y: rangeRect.bottom - editorRect.top
    };
}



function getTextEditorBoundaries() {
    const editorElement = document.querySelector('.text-editor-element');
    const editorRect = editorElement.getBoundingClientRect();
    console.log("Editor rect:", editorRect);
    return editorRect;
}

// Function to show the popup
function showPopup() {
    const caretPos = getCaretPosition();
    const editorRect = getTextEditorBoundaries();
    // Check if a valid caret position was obtained
    if (caretPos) {
        // Calculate the position relative to the editor
        let pop_up_boundary_left = caretPos.x;
        let pop_up_boundary_top = caretPos.y;

        // Get the popup dimensions
        const popupRect = popup.getBoundingClientRect();

        // Position the popup just above the caret
        pop_up_boundary_left = popupRect.width / 2; // Center horizontally
        pop_up_boundary_top = popupRect.height + 10; // Place above with a 10px gap

        // Ensure the popup stays within the editor boundaries
        pop_up_boundary_left = Math.max(editorRect.left, Math.min(pop_up_boundary_left, editorRect.right - popupRect.width));
        pop_up_boundary_top = Math.max(editorRect.top, pop_up_boundary_top);

        // Apply the calculated position
        popup.style.left = `${pop_up_boundary_left}px`;
        popup.style.top = `${pop_up_boundary_top}px`;
        popup.style.display = 'block';
    }
}

// Function to update popup position as caret moves
function updatePopupPosition() {
    if (popup.style.display === 'block') {
        showPopup();
    }
}

// Add event listener for caret movement
document.querySelector('.text-editor-element').addEventListener('keyup', updatePopupPosition);
document.querySelector('.text-editor-element').addEventListener('click', updatePopupPosition);






// Function to hide the popup
function hidePopup() {
    popup.style.display = 'none';
}

// Event listener for the command key
document.addEventListener('keydown', function (event) {
    // Check if the Command key (Mac) or Control key (Windows) is pressed
    if (event.metaKey || event.ctrlKey) {
        // Check if the 'k' key is pressed
        if (event.key === 'k') {
            event.preventDefault(); // Prevent default browser behavior
            if (popup.style.display === 'block') {
                hidePopup();
            } else {
                showPopup();
            }
        }
    }
});

// Event listener for the close button
document.getElementById('closePopup').addEventListener('click', hidePopup);

// Event listener to close the popup when clicking outside
document.addEventListener('click', function (event) {
    if (!popup.contains(event.target) && event.target !== popup) {
        hidePopup();
    }
});


// When user clicks generate , send data back to server
document.getElementById('promptForm').addEventListener('submit', function (e) {
    // Prevent the default form submission
    e.preventDefault();

    // Get the text from the prompt editor
    const promptText = document.getElementById('chatInput').value;

    // Send a POST request to the server with the prompt text
    fetch('/handle_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'prompt': promptText
        })
    })
        .then(response => {
            // Check if the response is ok, otherwise throw an error
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Log the successful response data
            console.log('Success:', data);
            // TODO: Handle the successful response (e.g., display a success message)

            // Clear the text field after successful submission
            document.getElementById('chatInput').value = '';
        })
        .catch(error => {
            // Log any errors that occur during the fetch
            console.error('Error:', error);
            // TODO: Handle the error (e.g., display an error message to the user)
        });
});
