# Standard library imports
from functools import wraps
import time
import random
import requests
from pydantic import BaseModel


def api_request(method):
    """
    Decorator for methods to handle HTTP requests with standardized error handling.

    Args:
        method (str): The HTTP method to use for the request (e.g. 'GET', 'POST),

    Returns:
        function: A wrapper function that executes the decorated method to obtain the request
            URL and data, performs the HTTP request, and returns the parsed JSON response
            or None if an error occurs.

    The decorated method should return a tuple (url, data), where 'data' may be None for methods
    that do not send a request body.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            url, data = func(self, *args, **kwargs)

            max_retries = 5
            backoff_base = 1

            for attempt in range(max_retries):
                try:
                    response = requests.request(method, url, headers=self.headers, data=data, timeout=10)

                    # Handle rate limiting explicitly
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")
                        try:
                            sleep_for = int(retry_after) if retry_after is not None else None
                        except ValueError:
                            sleep_for = None

                        if sleep_for is None:
                            sleep_for = backoff_base * (2 ** attempt) + random.random()

                        print(f"Rate limited (429). Retrying in {sleep_for:.1f}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(sleep_for)
                        continue

                    response.raise_for_status()
                    try:
                        return response.json()
                    except ValueError:
                        return response.text

                except requests.exceptions.RequestException as error:
                    resp = getattr(error, 'response', None)
                    status = getattr(resp, 'status_code', None) if resp is not None else None

                    # Retry on server errors (5xx)
                    if status and 500 <= status < 600 and attempt < max_retries - 1:
                        sleep_for = backoff_base * (2 ** attempt) + random.random()
                        print(f"Server error {status}. Retrying in {sleep_for:.1f}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(sleep_for)
                        continue

                    print(f"API request failed: {error}")
                    if 'response' in locals():
                        try:
                            print(response.text)
                        except Exception:
                            pass
                    return None

            print(f"Max retries exceeded for URL: {url}")
            return None
            
        return wrapper
    
    return decorator


def transform_childs_class(parent, child, class_type: BaseModel):
    """
    Transforms a child dictionary into an instance of the specified class type.
    This is required for Pydantic validation for the parent model.
    
    Args:
        parent (dict): The parent dictionary containing the child data.
        child (str): The key in the parent dictionary that holds the child data.
        class_type (type): The Pydantic model class to validate

    Returns:
        class_type: An instance of the specified class type with the child data.
    """
    if child in parent:
        try:
            new_class = class_type.model_validate(parent[child])
            parent[child] = new_class
            return parent[child]
        except Exception as e:
            print(f"Error transforming {child} to {class_type.__name__}: {e}")
    else:
        print(f"{child} not found in parent dictionary.")
    return None