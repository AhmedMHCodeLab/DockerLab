# Challenge Overview

## Prerequiste
🔹Linux
🔹Networking
🔹Docker
🔹Problem Solving
🔹Strictly NO AI !

## Resources
[Docs](https://docs.docker.com/guides/golang/build-images)

### Solution

The challenge was divided into two main tasks:

1. **Building Docker Containers:**  
    You needed to create Docker containers for the Go application and correctly assign environment variables.

2. **Troubleshooting a Curl Alias Issue:**  
    A hidden challenge involved a problematic `curl` alias in the `.bashrc` file, which caused a loop of fake errors. After investigating, the solution was to bypass the alias by using `/usr/bin/curl` directly to retrieve the required message.

This approach ensured both the application ran correctly in Docker and the curl command worked as intended.
