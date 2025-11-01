-- Idempotent PostgreSQL initialization for the auth service

-- Create role/user if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authuser'
   ) THEN
      CREATE ROLE authuser WITH LOGIN PASSWORD 'password123' CREATEDB;
   END IF;
END
$$;


-- Create extension used to create db conditionally
create extension dblink;


-- Create the auth database if it doesn't exist and set ownership to authuser
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_database WHERE datname = 'authdb'
    ) THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE authdb WITH OWNER authuser');
    END IF;
END $$;


-- Connect to the auth database with the authuser
\connect authdb authuser


-- Create the "user" table (quoted to match existing code that queries "user")
CREATE TABLE IF NOT EXISTS "users" (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);



