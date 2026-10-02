from tools.gmail import send_email


result = send_email(
    "aivon.chatbot@gmail.com",
    "Cognix Test",
    "This is a test email sent by Cognix."
)

print(result)