
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
    action.button.onclick = () => {
        const chain = editor.chain().focus()
        argument ? chain[command](argument).run() : chain[command]().run()
    }
})
unselectBase()

// Initial button state update
updateButtonStates()


// Prompt Editor
const promptEditor = new Editor({
    element: document.querySelector('.prompt-editor-element'),
    extensions: [StarterKit],
    content: '<p>....</p>',
})
