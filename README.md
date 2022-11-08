# FLASK + CELERY + REDIS + MONGODB + MONGO EXPRESS + NGINX : DOCKERIFIED

This is a basic container with the following:

    - Flask server
    - Celery worker using redis
    - MongoDB for storage
    - MongoExpress for easy viewing of Mongo data
    - All controlled with nginx so only ports 80 and 443 are exposed

## Instructions

1.  create a .env file with the same things as .env.example
2.  run `docker-compose up` in the same directory as the docker-compose.yml file
3.  profit

## Use cases

The current set up, the flask server waits for someone to send a get request to the /start route, and begins to send tasks (in this case get a random pokemon from pokeapi) to the celery worker. The Flask server then also checks the results
and saves them to a mongodb instance. You can then view the data at the /data route. Go to /stop to stop the workers.

- scan various ips and store the data for further analysis
- ping various APIs and store their results
- scrape webpages and store them

## Running in Production

Replace all dev env vars with production ones, including the flask_app/Dockerfile.dev in the docker-compose.yaml

Perhaps consider adding non-root users for the Redis and Celery containers.
