from flask import Flask, request, jsonify
import os
import subprocess

#app = Flask(__name__)

app = Flask(__name__, static_url_path='/static')

@app.route('/webhook-gh/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json

        # Verifique se é um push para o branch main
        if data.get('ref') == 'refs/heads/main':
            # Obtenha o nome do repositório
            repo_name = data['repository']['name']

            # Defina o caminho do script
            script_path = f'./scripts/{repo_name}.sh'

            # Verifique se o script existe
            if os.path.exists(script_path):
                try:
                    # Execute o script
                    result = subprocess.run([script_path], capture_output=True, text=True)
                    return jsonify({'message': 'Script executed successfully', 'output': result.stdout}), 200
                except subprocess.CalledProcessError as e:
                    return jsonify({'error': 'Script execution failed', 'output': e.output}), 500
            else:
                return jsonify({'error': 'Script not found'}), 404

        return jsonify({'message': 'Not a push to main branch'}), 200

    return jsonify({'message': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

