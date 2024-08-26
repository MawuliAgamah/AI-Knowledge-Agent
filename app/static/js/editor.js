
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


let editor = new Editor({
    element: document.querySelector('.text_editor_element'),
    extensions: [StarterKit,],
    content: '<p>....</p>',
    onTransaction({ editor }) {
        checkActive()
    }
})
selectBase("MenueBar") // Fill the menue-Bar
for (let i in actions) {
    let a = actions[i]  // get the command definition
    a.button = button(a.name)  // Create a button
    if (a.argument)
        a.button.onclick = () => editor.chain().focus()[a.command](a.argument).run()
    else
        a.button.onclick = () => editor.chain().focus()[a.command]().run()
}
unselectBase()

