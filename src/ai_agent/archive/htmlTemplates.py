css = '''

<style>

.chat-message {
padding: 1.5rem ; border-radius : 0.5rem ; margn-bottom: 1rem;display : flex
}

.chat-message.user {
    background-color : #2b313e
}

.chat-message.bot {
    background-colour : #475063
}


'''

bot_template = '''
<div class = "chat-message bot">
<div class = "avatar">
    <img src = "https://media.istockphoto.com/id/1409839764/vector/cute-little-robot-smiling-robotics-and-technology-kawaii-robot.jpg?s=612x612&w=0&k=20&c=qV3NO5VjN6UWdqWXDaKoFEAxt2o0ak0_jQRmM_JVGV4="style = "max-height :78px;max-width:78px;border-radius:50%;ohject-fit:cover;">
    <div>
    <div class = "message">{{$MSG}}</div>
<div>
'''

user_template = '''
<div class = "chat-message user">
<div class = "avatar">
    <img src = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Eo_circle_green_blank.svg/2048px-Eo_circle_green_blank.svg.png" style = "max-height :78px;max-width:78px;border-radius:50%;ohject-fit:cover;">
    <div>
    <div class = "message">{{$MSG}}</div>
<div>


'''
