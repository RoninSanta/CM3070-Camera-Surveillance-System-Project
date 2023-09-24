import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

sender_email = "testingsenderEmail@gmail.com"
sender_password = "3r4E$YW%5tjn@ZDN"
recipient_email = "josephshenfan@gmail.com"
subject = "Intruder Detected"
body = "An unrecognized human has been sighted on the premise, please check the image attached"

with open('screenshot.jpg', 'rb') as f:
    image_part = MIMEImage(f.read())
message = MIMEMultipart()
message['Subject'] = subject
message['From'] = sender_email
message['To'] = recipient_email
html_part = MIMEText(body)
message.attach(html_part)
message.attach(image_part)
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, message.as_string())
