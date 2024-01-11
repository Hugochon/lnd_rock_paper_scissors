# app.py
from flask import Flask, render_template, request, jsonify
from pyln.client import LightningRpc
import os
import random

app = Flask(__name__)

# Replace 'rpc_user', 'rpc_password', and 'rpc_path' with your LND node's actual details.
rpc_interface = LightningRpc("rpc_user:rpc_password@localhost:10009")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/result', methods=['POST'])
def result():
    user_choice = request.form['choice']
    choices = ['rock', 'paper', 'scissors']
    server_choice = random.choice(choices)

    result = determine_result(user_choice, server_choice)

    return render_template('result.html', user_choice=user_choice, server_choice=server_choice, result=result)

@app.route('/tip_page', methods=['POST'])
def tip_page():
    return render_template('tip_page.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    try:
        # Create a new Lightning invoice for 1 satoshi.
        invoice = rpc_interface.invoice(1, 'Tip for the game', '3600s')['bolt11']

        # Return the generated invoice to the frontend.
        return jsonify({'invoice': invoice})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_tip', methods=['POST'])
def process_tip():
    try:
        # Retrieve the Lightning invoice from the form data.
        invoice = request.form['invoice']

        # Query the Lightning Network to check the status of the invoice.
        payment_status = rpc_interface.getinvoice(invoice)['status']

        if payment_status == 'paid':
            # Invoice is paid, consider it as a successful tip.
            return "Tip processed successfully!"
        else:
            # Invoice is not paid, handle the case accordingly.
            return "Tip not yet paid. Please try again later."

    except Exception as e:
        return f"Error processing tip: {str(e)}"

def determine_result(user_choice, server_choice):
    if user_choice == server_choice:
        return 'Draw!'
    elif (
        (user_choice == 'rock' and server_choice == 'scissors') or
        (user_choice == 'paper' and server_choice == 'rock') or
        (user_choice == 'scissors' and server_choice == 'paper')
    ):
        return 'You Win!'
    else:
        return 'You Lose!'

if __name__ == '__main__':
    app.run(debug=True)
