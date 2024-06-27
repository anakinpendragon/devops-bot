#!/bin/sh
#requer instalação de dos2unix
export LANG=C.UTF-8

# Configurações
DB_PATH="instance/data.db"  # Caminho para o banco de dados SQLite
SCRIPTS_DIR="/usr/src/scripts/"
#CRON_DIR="./cron"
CRON_FILE="/etc/crontabs/root"

# Verifica se as pastas existem, se não, cria-as
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$CRON_DIR"

#repete o script de forma a ser um daemon
while true
do
      if [ -f /tmp/new ]; then	
	# Limpa o arquivo de crons anterior
	> "$CRON_FILE"
        rm -Rf $SCRIPTS_DIR/*
	# Lê os dados do banco de dados e gera os scripts e o arquivo de crons
	sqlite3 "$DB_PATH" "SELECT id, nome, cron, tipo, script FROM registro;" |
	while IFS='|' read -r id nome cron script tipo; do
  	# Verifica se todos os campos são válidos
  	 if [[ -n "$nome" && -n "$script" ]]; then
    	# Cria o arquivo de script
    	script_path="$SCRIPTS_DIR/$nome.sh"
    	#echo "$script" > "$script_path"
    	sqlite3 "$DB_PATH" "SELECT  script FROM registro where id=$id;" > $script_path
    	chmod +x "$script_path"
        dos2unix "$script_path"

    	# Adiciona a linha ao arquivo de crons
    	if [[ -n "$cron" ]];  	then
    	echo "$cron sh $script_path" >> "$CRON_FILE"
    	fi
  	fi
	done
	echo "Scripts and cron file generated successfully."
	rm -f /tmp/new
     fi	

sleep 0.2 

done
