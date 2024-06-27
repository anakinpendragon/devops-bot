from flask import Flask, render_template_string, redirect, url_for
import os
import subprocess

app = Flask(__name__)

# Path to the SSH public key
ssh_key_path = '/root/.ssh/id_rsa.pub'

# Function to read the public key
def read_ssh_key():
    try:
        with open(ssh_key_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "SSH key not found. Please generate a new key."

# Route to display the SSH public key
@app.route('/')
def index():
    key_content = read_ssh_key()
    return render_template_string('''
        <h1>SSH Public Key</h1>
        <pre>{{ key_content }}</pre>
        <form action="{{ url_for('generate_key') }}" method="post">
            <button type="submit">Generate New SSH Key</button>
        </form>
    ''', key_content=key_content)

# Route to generate a new SSH key
@app.route('/generate', methods=['POST'])
def generate_key():
    # Remove the existing SSH key files
    os.system('rm -f /root/.ssh/id_rsa /root/.ssh/id_rsa.pub')

    # Generate a new SSH key
    subprocess.run(['ssh-keygen', '-q', '-t', 'rsa', '-N', '', '-f', '/root/.ssh/id_rsa'], check=True)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

