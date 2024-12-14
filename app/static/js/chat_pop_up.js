

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





function getTextEditorBoundaries() {
    const editorElement = document.querySelector('.text-editor-element');
    const editorRect = editorElement.getBoundingClientRect();
    return editorRect;
}

function getCaretPosition() {
    const selection = window.getSelection();
    const editorElement = document.querySelector('.text-editor-element');

    if (!editorElement.contains(selection.anchorNode)) {
        return null;
    }

    if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        return {
            x: rect.x,
            y: rect.y,
            top: rect.top,
            bottom: rect.bottom
        };
    } else {
        // If there's no selection, return the editor's position
        const editorRect = editorElement.getBoundingClientRect();
        return {
            x: editorRect.x,
            y: editorRect.y,
            top: editorRect.top,
            bottom: editorRect.bottom
        };
    }
}


function drawBoundingBox() {

    const caretPos = getCaretPosition();
    const editorRect = getTextEditorBoundaries();
    let boundingBox = document.createElement('div');
    boundingBox.id = 'caretBoundingBox';
    document.body.appendChild(boundingBox);

    boundingBox.style.position = 'absolute';
    boundingBox.style.border = '2px solid red';
    boundingBox.style.left = `${editorRect.left}px`;
    boundingBox.style.top = `${caretPos.top}px`;
    boundingBox.style.pointerEvents = 'none';
    boundingBox.style.width = `${editorRect.width - 2}px`;
    boundingBox.style.height = `${(caretPos.bottom - caretPos.top) + 2}px`;
}

// Function to continuously update the bounding box
function updateBoundingBox() {
    const existingBox = document.getElementById('caretBoundingBox');
    if (existingBox) {
        existingBox.remove();
    }
    drawBoundingBox();
    requestAnimationFrame(updateBoundingBox);
}

// Start the continuous update
document.addEventListener('DOMContentLoaded', function () {
    updateBoundingBox();
});

// Add event listeners for user interactions that might change the caret position
document.querySelector('.text-editor-element').addEventListener('keyup', updateBoundingBox);
document.querySelector('.text-editor-element').addEventListener('click', updateBoundingBox);
document.querySelector('.text-editor-element').addEventListener('mouseup', updateBoundingBox);






// The idea here is that based on the  users caret 
// We find the HTML element above and below it
// If nothing below it then pop up will push elements down
// IF somethign below it we will push them up and down 

function BoundingBox() {
    const caretPos = getCaretPosition();
    const editorRect = getTextEditorBoundaries();
    let boundingBox = document.createElement('div');
    boundingBox.id = 'caretBoundingBox';
    document.body.appendChild(boundingBox);

    let box_left = `${editorRect.left}px`;
    let box_top = `${caretPos.top}px`;
    boundingBox.style.width = `${editorRect.width}px`;
    boundingBox.style.height = `${(caretPos.bottom - caretPos.top) + 2}px`;
}

function getClosestElementsToCare() {
    // Caret positinn
    const caretPos = getCaretPosition();
    box = BoundingBox()

    // Get the element above the caret
    const elementAbove = document.elementFromPoint(0, caretPos.y - 10);
    elementAbove.forEach(element => {
        console.log("Element above caret:", element);
    });

    // Get the element below the caret
    const elementBelow = document.elementFromPoint(0, caretPos.x, caretPos.y + 10);
    console.log("Element below caret:", elementBelow);

}
// Always run getClosestElementsToCare
document.addEventListener('DOMContentLoaded', function () {
    getClosestElementsToCare();
});

// Additionally, run it on any potential caret movement
document.querySelector('.text-editor-element').addEventListener('keyup', getClosestElementsToCare);
document.querySelector('.text-editor-element').addEventListener('click', getClosestElementsToCare);
document.querySelector('.text-editor-element').addEventListener('mouseup', getClosestElementsToCare);



// Function to show the popup
function showPopup() {
    const caretPos = getCaretPosition();
    const editorRect = getTextEditorBoundaries();
    // Check if a valid caret position was obtained
    if (caretPos) {
        // Calculate the position relative to the editor
        let pop_up_boundary_left = caretPos.x;
        let pop_up_boundary_top = caretPos.y;

        const elementAtCaret = document.elementFromPoint(caretPos.x, caretPos.y);

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


// Move the User written text when the menu pops us 
function adjustTextEditorMargin() {
    const textDiv = document.getElementById('text-editor-element_id');
    const chatPopup = document.querySelector('.chat-popup');

    // Check if the chat popup exists and is currently displayed
    if (chatPopup.style.display === 'block') {
        textDiv.style.marginTop = '100px';
    } else {
        textDiv.style.marginTop = '0px';
    }
}

// Call the function initially to set the correct margin
adjustTextEditorMargin();
