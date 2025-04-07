# Caching Proxy Server
A lightweight Python-based HTTP proxy server that caches responses from a target API

## Features
- A CLI using prompt "--port <port> --origin <url>" to start a caching server on specific port and forward requests to <url>
- Forwards HTTP GET requests to a chosen port by user
- Caches responses to REDIS and returns HTTP responses to user

## Getting Started

### Prerequisities 
- Python 3.7+
- Requires installation of redis (besides that, no other external libraries required)

### Running the server
python proxy_server.py

## Testing
Use "curl" to test caching behavior
----------------------------------
curl -i https://localhost:3000/products
- above should forward the request to your request URL and cache it / send back the response to user
