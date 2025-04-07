import socket
import re
import validators
import redis_client



def main() -> None:

    # Determines whether or not a connection on a port has started for our application yet
    STARTED = False

    """
    We print our CLI prompt and prompts user for input in the correct format "--port <number> --origin <url>", 
    """
    # Socket is created 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Prompts user for input (looking for what port to run on)
    while not STARTED:

        # Grabs user input 
        user_input = input("caching-proxy ")

        # Splits user input by space (default)
        split_input = user_input.split()

        # checks arguments of the input
        if (check_input(split_input=split_input)):

            # binds our socket with specific port            
            server_socket.bind(("0.0.0.0", int(split_input[1])))

            # connects to users request url/website
            server_socket.connect(split_input[3], 80)

            # sets variable STARTED to true so application knows we found a port
            STARTED = True

        # continues the loop
        print("To start the caching proxy application, please enter your input in following format: \"--port <number> --origin <url>\"\n----------------------------------------------------------")
        continue

    # we let our socket listen for incoming connections
    server_socket.listen(5)

    # print "waiting for connection"
    print("Waiting for requests...")

    # Starts another loop to handle client requests
    while True:
        try:

            # Accepts connection from a request
            client_socket, address = server_socket.accept()

            # prints request accepted
            print(f"Request accepted from {address}")

            # Grab data from request and decodes it at the same time into comprehensible string
            data = client_socket.recv(4096).decode()
            if not data:
                print("Client disconnected.")
                continue

            # Grabs the given path in the GET request, and forwards request
            split_data = data.split()
            
            # our request we are forwarding - "GET URL/REQUEST ..."
            new_request = f"GET {split_data[1]} HTTP/1.1\r\nHost: {split_input[3]}\r\n\r\n"

            # check cache first if response is already stored there
            cached_response = redis_client.get(new_request)
            if not cached_response:

                # forwards request 
                server_socket.sendall(new_request)

                # An empty byte object to store the response
                response = b""

                # loops until all data is collected
                while True:
                    chunk = server_socket.recv(4096)
                    if not chunk:
                        break

                    # adds chunk of data to response
                    response += chunk

                # cache the response and return it to original sender
                redis_client.set(new_request, response)

                # adds header
                new_response = add_hit_header(response, False)

                # send back to original client
                client_socket.sendall(response.encode())

                # continues
                continue

            # if cached we add the header
            response = add_hit_header(cached_response, True)

            # Send back to client
            client_socket.sendall(response.encode())

        except:
            print("Error has occured with the socket. Try again later.")


def add_hit_header(response: str, hit: bool) -> str:

    """
    This method adds a header (X-Cache: hit/miss) based on whether the response is from cache or original server
    """

    # modify the header to indicate we are sending a response from origin server
    header, body = response.split("\r\n\r\n", 1)

    if hit:
        
        # adds the miss hit to our header
        header +=  "\r\nX-Cache: MISS"

    else:

        # adds hit to our header
        header += "\r\nX-Cache: HIT"

    # combine everythin again
    new_response = header + "\r\n\r\n" + body

    # return new response
    return new_response


def check_input(split_input: str) -> bool:

    """
    This method takes users split input and checks if each argument is valid or not
    """

    # We are expecting four arguments, if not 4 then we raise an error
    try:
        if len(split_input) != 4:
            raise ValueError(f"expected 4 arguments with format: --port <port_number> --origin <url>")
            
        # goes through each argument to see if arguments matches correct format
        if (split_input[0] != "--port"):
            raise ValueError(f"First argument should be \"--port\".")
            
        # removes "-" in order to check if second argument is a number
        port_number = re.sub("^-", "", split_input[1])
        if not str.isdigit(port_number):
            raise ValueError(f"Second argument should be a port number. Try again.")
            
        # Third argument should be --origin
        if (split_input[2] != "--origin"):
            raise ValueError(f"Third argument should be \"--origin\".")
            
        # Ensures last argument is a valid website
        if not validators.url(split_input[3]):
            raise ValueError(f"Fourth argument is not a valid url. Please try again.")

        # Returns true if input passes all checks
        return True
                    
    except ValueError as e:
            print(f"Error: {e}")
            return False

# Starts application
if __name__ == "__main__":
    main()