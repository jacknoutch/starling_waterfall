# Standard library imports
from functools import wraps
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

            try:
                response = requests.request(method, url, headers=self.headers, data=data)
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as error:
                print(f"API request failed: {error}")
                print(response.text)
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