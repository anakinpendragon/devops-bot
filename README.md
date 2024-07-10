This project aim to create a simple and light task manager. Jenkins is too expensive in processor and memory .
The aim is create a web interface to create jobs , run jobs through crons , webhook or manualy, and see logs from jobs.
This jobs are made in shell script.


DEVOPS Bot is made with python, flask, bash, sqlite, and use https://simplecss.org/
as css theme.

Para executar um script via webhook faça como no exemplo:

curl -X POST http://localhost:8080/webhook/   -H "Content-Type: application/json"  -d '{"key": "chave", "script_name": "teste1"}'
