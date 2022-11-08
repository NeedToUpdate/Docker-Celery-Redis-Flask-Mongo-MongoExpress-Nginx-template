#creates a non-root user so we dont use root priviledges with our app just in case
mongosh admin --host localhost -u root -p pass --eval "db.createUser({user: '$MONGODB_USERNAME', pwd: '$MONGODB_PASSWORD', roles: [{role: 'readWrite', db: '$MONGODB_DATABASE'}]});"
echo "Mongo users created."