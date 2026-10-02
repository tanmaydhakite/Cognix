def calculate(expression: str) -> dict:
    """
    Calculate a basic mathematical expression.

    Args:
        expression: A mathematical expression such as
                    "25 * 4" or "100 / 5".

    Returns:
        A dictionary containing the calculation result.
    """

    try:
        # Basic calculator for our first prototype.
        # We will make this safer later.
        result = eval(expression, {"__builtins__": {}}, {})

        return {
            "success": True,
            "expression": expression,
            "result": result
        }

    except Exception as error:

        return {
            "success": False,
            "expression": expression,
            "error": str(error)
        }