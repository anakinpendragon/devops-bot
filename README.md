This project aim to create a simple and light task manager. Jenkins is too expensive in processor and memory .
The aim is create a web interface to create jobs , run jobs through crons , webhook or manualy, and see logs from jobs.
This jobs are made in shell script.


DEVOPS Bot is made with python, flask, bash, sqlite, and use https://simplecss.org/
as css theme.

To run a script with webhook, use like this example:

curl -X POST http://localhost:8080/webhook/   -H "Content-Type: application/json"  -d '{"key": "chave", "script_name": "teste1"}'


This project is made to run with docker compose in linux alpine. To you just need to write in shell: \\

#docker compose build 

#docker compose up \\
