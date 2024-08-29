
import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'

const actions = [
    { name: "bold", command: 'toggleBold', disable: true },
    { name: "italic", command: 'toggleItalic', disable: true },
    { name: "strike", command: 'toggleStrike', disable: true },
    { name: "code", command: 'toggleCode', disable: true },
    { name: "clear marks", command: 'unsetAllMarks' },
    { name: "clear nodes", command: 'setParagraph' },
    { name: "paragraph", command: 'toggle' },
    { name: "h1", command: 'toggleHeading', argument: { level: 1 } },
    { name: "h2", command: 'toggleHeading', argument: { level: 2 } },
    { name: "h3", command: 'toggleHeading', argument: { level: 3 } },
    { name: "h4", command: 'toggleHeading)', argument: { level: 4 } },
    { name: "h5", command: 'toggleHeading', argument: { level: 5 } },
    { name: "h6", command: 'toggleHeading', argument: { level: 6 } },
    { name: "bullet list", command: 'toggleBulletList' },
    { name: "ordered list", command: 'toggleOrderedList' },
    { name: "code block", command: 'toggleCodeBlock' },
    { name: "blockquote", command: 'toggleBlockquote' },
    { name: "horizontal rule", command: 'setHorizontalRule' },
    { name: "hard break", command: 'setHardBreak' },
    { name: "undo", command: 'undo', disable: true },
    { name: "redo", command: 'redo', disable: true }
]

// Check activation status of buttons
function updateButtonStates() {
    actions.forEach(action => {
        const { button, disable, name, command } = action

        // Update disabled state
        if (disable) {
            button.disabled = !editor.can().chain().focus()[command]().run()
        }

        // Update active state
        const isActive = editor.isActive(name)
        button.classList.toggle('is-active', isActive)
    })
}


// Create editor instance
const editor = new Editor({
    element: document.querySelector('.text-editor-element'),
    extensions: [StarterKit],
    content: '<p>....</p>',
    onTransaction: updateButtonStates
})

// Populate menu bar with action buttons
selectBase("editor-menu-bar")
actions.forEach(action => {
    const { name, command, argument } = action
    action.button = button(name)
    action.button.classList.add('editor-action-button') // Add a common class to all buttons
    action.button.onclick = () => {
        const chain = editor.chain().focus()
        argument ? chain[command](argument).run() : chain[command]().run()
    }
})
unselectBase()
updateButtonStates() // Initial button state update


// Prompt Editor
const promptEditor = new Editor({
    element: document.querySelector('.prompt-editor-element'),
    extensions: [StarterKit],
    content: '<p>....</p>',
})



// Helper text functionality
const helperText = document.createElement('div');
helperText.className = 'helper-text';
helperText.style.position = 'absolute';
helperText.style.display = 'none';
document.body.appendChild(helperText);


// Function to get caret position
function getCaretPosition() {
    const selection = window.getSelection();
    const range = selection && selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
    if (!range) {
        console.warn('No valid selection range found');
        return { x: 0, y: 0 };
    }
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(document.querySelector('.text-editor-element'));
    preCaretRange.setEnd(range.endContainer, range.endOffset);
    const rect = preCaretRange.getBoundingClientRect();

    const x = rect.right;
    const y = rect.bottom;

    console.log("Caret Position x pos:", x, "Caret Position y pos:", y);

    return { x, y };
}

// Function to update helper text position and content
function updateHelperText(view) {
    const { state } = view;
    const { selection } = state;
    const { from } = selection;

    // Get the cursor coordinates using getCaretPosition
    const caretPos = getCaretPosition();

    helperText.textContent = '⌘ + k to chat';
    helperText.style.display = 'block';
    helperText.style.color = 'grey';  // Set the text color to grey

    const cursorWidth = 2;   // Cursor width is approximated
    const padding = 5;       // Add some padding


    // Position to the right of the cursor
    helperText.style.position = 'absolute';
    helperText.style.left = `${caretPos.x}px`;
    helperText.style.top = `${caretPos.y}px`;

    // Get the parent container with class 'text-editor-element'
    const editorElement = document.querySelector('.text-editor-element');
    const editorRect = editorElement.getBoundingClientRect();

    // Ensure the helper text doesn't go off-screen to the right
    const helperTextRect = helperText.getBoundingClientRect();
    if (helperTextRect.right > editorRect.right) {
        helperText.style.left = `${relativeLeft - helperTextRect.width - padding}px`;
    }

    // Append the helper text to the parent container if it's not already there
    if (!editorElement.contains(helperText)) {
        editorElement.appendChild(helperText);
    }
}

// Show helper text when the editor gains focus
editor.on('focus', ({ editor, event }) => {
    updateHelperText(editor.view);
});



// Hide helper text when the editor loses focus
editor.on('blur', () => {
    helperText.style.display = 'none';
});

// Update helper text position when the cursor moves
editor.on('selectionUpdate', ({ editor }) => {
    if (editor.isFocused) {
        updateHelperText(editor.view);
    }
});

// Update helper text position when the content changes
editor.on('update', ({ editor }) => {
    if (editor.isFocused) {
        // Check if the content has changed
        if (editor.state.doc.content !== editor.state.doc.type.createAndFill().content) {
            helperText.style.display = 'none';
        } else {
            updateHelperText(editor.view);
        }
    }
});

// Hide helper text when user starts typing
editor.on('transaction', ({ transaction }) => {
    if (transaction.docChanged) {
        helperText.style.display = 'none';
    }
});



// Handle Highlighted Text and send that to the language model 

