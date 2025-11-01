FROM postgres:17-alpine

# Defaults for Postgres environment variables
# ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
# ENV POSTGRES_DB=postgres

# Copy initialization scripts 

# if using docker
# COPY ./init.sql /docker-entrypoint-initdb.d/

# if using docker-compose
COPY ./postgres/init.sql /docker-entrypoint-initdb.d/


EXPOSE 5432