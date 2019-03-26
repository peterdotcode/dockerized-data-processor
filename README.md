# dockerized-data-processor

##Setup

Run the below commands to create the docker container. Allow a couple of minutes to build the container builds conda 4.6.8.

'''
cd dockerized-data-processor
docker build -t peter_dowling_assignment .
docker run --name v1 -p 8888:8888 -v "$PWD:/opt/notebooks" -d v1
'''

Once build complete and running open <http://localhost:8888> use the **password:** _root_

