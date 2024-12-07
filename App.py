from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import os
from twilio.rest import Client
import random

# Load environment variables from .env file
load_dotenv()

# Access the credentials from the environment variables
TWILIO_ACCOUNT_SID = os.getenv('ACa4aa9efce86d1ed0003870008951b8')
TWILIO_AUTH_TOKEN = os.getenv('5615bca03c788eb9de226787887868')
TWILIO_PHONE_NUMBER = os.getenv('9980798902')

# Check if the environment variables are loaded correctly
print("Twilio Account SID:", TWILIO_ACCOUNT_SID)
print("Twilio Auth Token:", TWILIO_AUTH_TOKEN)
print("Twilio Phone Number:", TWILIO_PHONE_NUMBER)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# A dictionary to store users temporarily
users = {}

# Home page
@app.route('/')
def home():
    return render_template('home.html')


# Main page - where the user enters their details
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        full_name = request.form['full_name']
        adhar_number = request.form['adhar_number']
        phone_number = request.form['phone_number']

        # Generate a secure OTP
        otp = random.randint(1000, 9999)

        # Store the user's details and OTP in the dictionary (for security)
        users[phone_number] = {'name': full_name, 'adhar_number': adhar_number, 'otp': otp}

        # Send OTP to the user's phone using Twilio
        try:
            message = client.messages.create(
                body=f"Your OTP is: {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            flash(f"OTP sent to {phone_number}.", 'info')
        except Exception as e:
            flash(f"Failed to send OTP: {str(e)}", 'danger')

        # Redirect to OTP verification page
        return redirect(url_for('otp_popup', phone_number=phone_number))

    return render_template('main_page.html')


# OTP verification page
@app.route('/otp/<phone_number>', methods=['GET', 'POST'])
def otp_popup(phone_number):
    if request.method == 'POST':
        entered_otp = request.form['otp']

        # Verify the OTP
        if phone_number in users and int(entered_otp) == users[phone_number]['otp']:
            flash("OTP verified successfully!", 'success')
            return redirect(url_for('user_vote', phone_number=phone_number))
        else:
            flash("Invalid OTP. Please try again.", 'danger')

    return render_template('otp_popup.html', phone_number=phone_number)


# User vote page
@app.route('/user_vote/<phone_number>', methods=['GET', 'POST'])
def user_vote(phone_number):
    user = users.get(phone_number)

    if not user:
        flash("User not found. Please start again.", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        vote_for = request.form['vote_for']
        # Store the vote in the dictionary (here we're just printing it)
        print(f"Vote for {user['name']} ({user['adhar_number']}): {vote_for}")

        # Store the vote in the user's data
        users[phone_number]['vote_for'] = vote_for

        flash("Congratulations for using your vote!", 'success')
        return redirect(url_for('main_page'))

    return render_template('vote_page.html', user=user)


# Demo vote page
@app.route('/demo_vote/<phone_number>', methods=['GET', 'POST'])
def demo_vote(phone_number):
    user = users.get(phone_number)

    if not user:
        flash("User not found. Please start again.", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        vote_for = request.form['vote_for']
        # Store the demo vote in the dictionary (here we're just printing it)
        print(f"Demo Vote for {user['name']} ({user['adhar_number']}): {vote_for}")

        # Store the demo vote in the user's data
        users[phone_number]['demo_vote_for'] = vote_for

        flash("Congratulations! Your demo vote has been recorded.", 'success')
        return redirect(url_for('main_page'))

    return render_template('demo_vote.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
