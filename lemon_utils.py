from keys_config import *

import smtplib
from email.mime.multipart import MIMEMultipart # standard python library
from email.mime.text import MIMEText
from twilio.rest import Client

twilio_client = Client(Twilio_account_SID, Twilio_token)#  Send the message


def check_market_open(lemon_client):
    if not lemon_client.market_data.venues.get('XMUN').results[0].is_open:
        opening_days = lemon_client.market_data.venues.get('XMUN').results[0].opening_days
        if dt.date.today() not in opening_days:
            next_day = opening_days[1]
            message = f"Exchange is closed today. Next trading day is on {next_day.strftime('%A')} {next_day.strftime('%d-%m-%Y')}"
            inform(message)
            return message
        # check time
        market_start_time = dt.datetime.now().replace(hour=8, minute=00, second=00)
        market_end_time = dt.datetime.now().replace(hour=22, minute=00, second=00)
        right_now = dt.datetime.now()
        if market_end_time < right_now:
            return "Exchange is already closed for today, No trades are possible"
        elif market_start_time > right_now:
            return f"Exchange is still closed. Try in {int((market_start_time - right_now).total_seconds()//3600)} hours"
    return 'open'

def inform(message_to_send):
    message = twilio_client.messages.create(
                              body=message_to_send,
                              from_=Twilio_phone,
                              to=Reciep_Phone
                          )
    print(message_to_send)

def send_email(mail_subject, df_test):
    msg = MIMEMultipart() #Setup the MIME
    msg['From'] = 'Lemon Paper'
    msg['To'] = receiver_address
    msg['Subject'] = mail_subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() #enable security
    server.login(sender_address, sender_pass) # login with mail_id and password

    html = """\
    <html>
    <head></head>
    <body>
        {0}
    </body>
    </html>
    """.format(df_test.to_html())
    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    server.sendmail(sender_address, receiver_address, msg.as_string())
    server.quit()


def read_gs_starategy_setting():
    '''read strategy settings (allocated capital, SL, universe, etc.) from google sheet'''
    pass