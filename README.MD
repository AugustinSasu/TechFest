# Build and run the DB Container:

docker compose up -d

# Install requirements:

pip install -r requirements.txt

# Copy the sql scripts into the container:

cd ./sql

docker cp 01_users_roles.sql vw-db:/tmp/01_users_roles.sql

docker cp 02_schema.sql vw-db:/tmp/02_schema.sql

docker cp 03_populate.sql vw-db:/tmp/03_populate.sql

docker cp 04_vector_index.sql vw-db:/tmp/04_vector_index.sql

cd ..

# Enter container bash:

docker exec -it vw-db bash

# Enter SQL Plus:

sqlplus / as sysdba

# Run the script as sys:

@/tmp/01_users_roles.sql

@/tmp/02_schema.sql

@/tmp/03_populate.sql

@/tmp/04_vector_index.sql

exit

exit

# (Optional) Run the python scripts, if you want to use embeddings and run the API

cd ./etl

python load_embeddings.py

cd ..

python api.py

# To rebuild:

docker-compose down

docker volume rm vwdb_vwvolume (run docker volume ls to see your volume name)

and repeat the steps above