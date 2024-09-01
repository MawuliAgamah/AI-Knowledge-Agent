
import { Editor, Node } from 'https://esm.sh/@tiptap/core'
import { StarterKit } from 'https://esm.sh/@tiptap/starter-kit'

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

// Check Activation of buttons
function checkActive() {
    for (let i in actions) {
        let a = actions[i]  // 
        if (a.disable) {
            if (editor.can().chain().focus()[a.command]().run())
                a.button.removeAttribute("disabled")
            else
                a.button.setAttribute("disabled", "true")
        }
        if (a.button.classList.contains('is-active')) {
            if (!editor.isActive(a.name)) a.button.classList.remove('is-active')
        } else
            if (editor.isActive(a.name)) a.button.classList.add('is-active')
    }
}







// create editor instance
const editor = new Editor({
    element: document.querySelector('.text-editor-element'),
    extensions: [
        StarterKit,
    ],
    content: '<div></div>', // Always start with a div
    autofocus: true,
    injectCSS: false,
    onTransaction({ state }) {
        checkActive()
        updateButtonStates()


    },
})


// Make the height of the text editor element the same as its parent, accounting for padding
function adjustEditorHeight() {
    const editorElement = document.getElementById('text-editor-element_id');
    const parentElement = editorElement.parentElement;

    if (editorElement && parentElement) {
        const parentStyle = window.getComputedStyle(parentElement);
        const parentPaddingTop = parseFloat(parentStyle.paddingTop);
        const parentPaddingBottom = parseFloat(parentStyle.paddingBottom);
        const parentHeight = parentElement.clientHeight - parentPaddingTop - parentPaddingBottom;

        editorElement.style.height = `${parentHeight}px`;
    }
}
// Call the function initially
adjustEditorHeight();

// Add event listener for window resize
window.addEventListener('resize', adjustEditorHeight);

// If the parent's height might change dynamically, you may need to call this function
// at appropriate times or set up a MutationObserver to watch for changes


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

// Helper text functionality
const helperText = document.createElement('div');
helperText.className = 'helper-text';
helperText.style.position = 'absolute';
helperText.style.display = 'none';
document.body.appendChild(helperText);

// update the updateHelperText function
function updateHelperText() {
    const caretPos = getCaretPosition(); // 
    if (caretPos.x != 0 && caretPos.y != 0) {
        helperText.textContent = '⌘ + k to chat';
        helperText.style.display = 'block';
        helperText.style.color = 'grey';

        const padding = 5;
        // Position to the right of the cursor
        helperText.style.position = 'absolute';
        helperText.style.left = `${caretPos.x + 20}px`;
        helperText.style.top = `${caretPos.y + 60}px`;

    } else {
        helperText.textContent = '⌘ + k to chat';
        helperText.style.display = 'block';
        helperText.style.color = 'grey';

        const padding = 5;
        // Position to the right of the cursor
        helperText.style.position = 'absolute';
        helperText.style.left = `${caretPos.x}px`;
        helperText.style.top = `${caretPos.y}px`;
    }
}
updateHelperText();


// Show helper text when the editor gains focus
editor.on('focus', ({ editor, event }) => {
    updateHelperText();
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



// Hide helper text when user starts typing
//editor.on('transaction', ({ transaction }) => {
//    if (transaction.docChanged) {
//helperText.style.display = 'none';
//  }
//});



// Handle Highlighted Text and send that to the language model 

