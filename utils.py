from pydantic import BaseModel


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