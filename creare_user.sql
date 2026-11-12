CREATE USER trading_user WITH PASSWORD '624255';
ALTER ROLE trading_user SET client_encoding TO 'utf8';
ALTER ROLE trading_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE trading_user SET timezone TO 'Europe/Bucharest';

GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;
GRANT ALL ON SCHEMA public TO trading_user;