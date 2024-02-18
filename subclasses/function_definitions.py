import inspect

# Import the functions from functions.py
from subclasses import functions

class FunctionDefinitionGenerator:

    @staticmethod
    def generate_definitions(module):
        definitions = []

        type_mapping = {
            "int": "integer",
            "float": "number",
            "str": "string",
            "bool": "boolean",
            "list": "array",
            "tuple": "array",
            "dict": "object",
            "None": "null",
        }

        # Get all the functions from the module
        methods = [func for func in module.__dict__.values() if inspect.isfunction(func)]

        for method in methods:
            parameters = inspect.signature(method).parameters

            param_names = list(parameters.keys())

            param_types = {}
            for name in param_names:
                annotation_str = str(parameters[name].annotation)
                if "'" in annotation_str:
                    type_name = annotation_str.split("'")[1]
                else:
                    type_name = annotation_str
                param_types[name] = type_mapping.get(type_name, 'string')

            if 'steps_remaining' in param_names:
                param_names.remove('steps_remaining')

            function_definition = {
                "name": method.__name__,
                "description": inspect.getdoc(method),
                "parameters": {
                    "type": "object",
                    "properties": {
                        param: {
                            "type": param_types[param],
                            "description": f"The {param} of the {method.__name__}."
                        } for param in param_names
                    },
                    "required": param_names,
                    "requirements_for_response": "Please respond ONLY with valid json that conforms to JSON schema. Do not include additional text other than the object json as we will load this object with json.loads() and pydantic.",
                }
            }

            function_definition["parameters"]["properties"]["steps_remaining"] = {
                "type": "string",
                "description": "detailed description of the remaining steps in this flow with subtasks. 'all steps completed' if all steps are complete."
            }

            function_definition["parameters"]["required"].append("steps_remaining")

            definitions.append(function_definition)
        return definitions

    @staticmethod
    def generate_function_mapping(module):
        return {func.__name__: func for func in module.__dict__.values() if inspect.isfunction(func)}

# Generate and set the function definitions
function_definitions = FunctionDefinitionGenerator.generate_definitions(functions)
# Generate and set the function mapping
function_mapping = FunctionDefinitionGenerator.generate_function_mapping(functions)

# save the function definitions to a file
with open('function_def.py', 'w') as outfile:
    outfile.write(f"function_definitions = {function_definitions}")
