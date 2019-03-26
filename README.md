# dockerized-data-processor
Live Juypter notebook demo available here:

<https://ec2-63-32-55-21.eu-west-1.compute.amazonaws.com:8888/>

Please contact me directly for the password

_The site does not contain a valid SSL cert so you will need to click show details on the bottom left and press **proceed/continue**_
## Setup

Run the below commands to create the docker container. Allow a couple of minutes to build the container builds conda 4.6.8.

```
cd dockerized-data-processor
docker build -t peter_dowling_assignment .
docker run --name v1 -p 8888:8888 -v "$PWD:/opt/notebooks" -d v1
```

Once build complete and running open <http://localhost:8888> use the **password:** _root_

## Scheduling the data processor

Setup the below to command to run on the host os scheduler:

```
docker exec -w /opt/notebooks <container_id> python /opt/notebooks/setup.py

```
Example using cron scheduler run everyday at midnight:
```
0 0 * * * docker exec -w /opt/notebooks <container_id> python /opt/notebooks/setup.py

```
