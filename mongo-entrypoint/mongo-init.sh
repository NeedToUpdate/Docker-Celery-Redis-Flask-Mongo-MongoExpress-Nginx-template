#!/usr/bin/bash

set -e

use $MONGO_INITDB_DATABASE

mongosh admin --host localhost -u root -p pass --eval "db.createUser({user: '$MONGODB_USERNAME', pwd: '$MONGODB_PASSWORD', roles: [{role: 'readWrite', db: '$MONGODB_DATABASE'}]});"
echo "Mongo users created."