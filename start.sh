touch /tmp/new
crond
gunicorn --bind 0.0.0.0:8080 main:app  --timeout 600 &
./update-scripts.sh 

