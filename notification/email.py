import smtplib, os
from email.message import EmailMessage

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_HOST = os.environ.get("SMTP_HOST")


def notification_mail(message):
    try:
        mp3_fid = message["mp3_fid"]
        receiver_address = message["username"]
        sender_address = "Private Person <from@example.com>"

        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg["Subject"] = "MP3 Download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP(SMTP_HOST, 587)
        session.starttls()
        session.login(SMTP_USERNAME, SMTP_PASSWORD)
        session.send_message(msg, sender_address, receiver_address)
        session.quit()
        print(f"📧 Email sent to {receiver_address} for mp3_fid: {mp3_fid}")
    except Exception as err:
        print("Error occurred while sending email")
        print(err)

