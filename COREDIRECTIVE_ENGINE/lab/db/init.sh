#!/usr/bin/env bash
# Runs once, on the first start of lab-db, inside the postgres image. Creates
# one database and one role each for BloodHound and Keycloak from lab.env
# (BH_DB_PASS, KC_DB_PASS). No password is written anywhere else.
set -euo pipefail
: "${BH_DB_PASS:?BH_DB_PASS missing from lab.env}"
: "${KC_DB_PASS:?KC_DB_PASS missing from lab.env}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<SQL
CREATE ROLE bloodhound LOGIN PASSWORD '${BH_DB_PASS}';
CREATE DATABASE bloodhound OWNER bloodhound;
CREATE ROLE keycloak LOGIN PASSWORD '${KC_DB_PASS}';
CREATE DATABASE keycloak OWNER keycloak;
SQL
