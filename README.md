# Weather Station Simulation

-----
This project simulates several (~10) networked weather stations that gather data and communicate with a server for aggregation. The project is an assignment for the Communications Lab 2 class of 2025-2026 at ECE, University of Patras.
More info in the project description [here](project_description.pdf)

## Instructions

----

- For Windows 10 and 11, the project is built by running the build script found [here](build.ps1). To run Docker containers in Windows, [Docker Desktop](https://www.docker.com/products/docker-desktop/) is required
- For Linux, the bash script found [here](build.sh) *should* work, but it hasn't been tested.

The scripts handle building the containers and the volumes needed, based on the docker compose files provided. The scripts can be modified to change the behavior of each station, for example by enabling or disabling different metrics in each station or changing the interval between packets sent to the server. The server and the weather stations are in an isolated "bridge" docker network, and they cannot be interacted with directly outside of this network. Received metrics are written to a database volume, which is then accessed by the web interface [here](http://127.0.0.1:8080/?). The server also creates logs of received packets and stores them in a separate docker volume in JSON format.
