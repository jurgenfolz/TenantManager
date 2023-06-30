def api_error(status_code: Exception):
    status_code = int(str(status_code))
    if status_code != 200:
        if status_code == 400:
            return f"{status_code}: Bad Request. The request was malformed or invalid."
        elif status_code == 401:
            return f"{status_code}: Unauthorized. The request requires authentication and the client did not provide valid credentials."
        elif status_code == 403:
            return f"{status_code}: Forbidden. The client does not have permission to access the requested resource."
        elif status_code == 404:
            return f"{status_code}: Not Found. The requested resource could not be found on the server."
        elif status_code == 429:
            return f"{status_code}: Too Many Requests. The client has sent too many requests."
        elif status_code == 500:
            return f"{status_code}: Internal Server Error. The server encountered an error while processing the request."
        else:
            return f"Request failed with status code {status_code}"
    elif status_code == 200:
        return "Success"