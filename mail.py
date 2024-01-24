import requests
import configparser
import json

# Load configuration file
config = configparser.ConfigParser()
config.read('key_config.ini')

GMAIL_ADDRESS = config['DEFAULT1']['GMAIL_ADDRESS']
GMAIL_NAME = config['DEFAULT1']['GMAIL_NAME']
BREVO_API = config['DEFAULT1']['BREVO_API']


def sendMail(address,generated_otp):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API,
        "content-type": "application/json"
    }
    payload = {
        "sender": {
            "name": GMAIL_NAME,
            "email": GMAIL_ADDRESS
        },
        "to": [
            {
                "email": address,
            }
        ],
        "subject": "OTP Verification",
        "htmlContent": f'''<!DOCTYPE html>
                            <html>
                            <head>
                                <title>OTP Verification</title>
                            </head>
                            <body>
                                <h3>OTP Verification</h3>
                                <p>Hello USER,</p>
                                <p>Your One-Time Password (OTP) for verification is: <strong>{generated_otp}</strong></p>
                                <p>Please use this OTP to complete your verification process. This OTP will expire in 30 minutes.</p>
                                <p>If you did not request this OTP, please ignore this email.</p>
                                <p>Thank you for using our service!</p>
                                <p>Best regards,<br>Library Genesis</p>
                            </body>
                            </html>
                        ''' 
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    sent=True
    if response.status_code == 200 or response.status_code == 201:
        sent=True
        r=f"OTP sent successfully to {address}. Enter the otp received for verification!"
    else:
        d1=response.text
        d=json.loads(d1)
        err=d.get("message")
        #r=f"Failed to send OTP!. Status code: {response.status_code},{err} "
        r=f"Failed to send OTP!. {err} "
        
        sent=False
    return r


def verifyMail(entered_otp, generated_otp):
       
    # Ensure both OTPs are of the same length
    if len(entered_otp) != len(generated_otp):
        return False
    # Constant-time comparison to prevent timing attacks
    result = 0
    for a, b in zip(entered_otp, generated_otp):
        result |= ord(a) ^ ord(b)

    return result == 0



