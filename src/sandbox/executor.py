import sys
import io
import contextlib
import traceback

class SandboxExecutor:
    def __init__(self):
        self.allowed_modules = ['math', 'datetime', 'json']

    def execute(self, code, context_variables={}):
        """
        Executes the provided Python code in a restricted environment.
        
        Args:
            code (str): The Python code to execute.
            context_variables (dict): Variables to inject into the execution scope.
            
        Returns:
            dict: {'success': bool, 'result': any, 'stdout': str, 'error': str}
        """
        # Capture stdout
        stdout_capture = io.StringIO()
        
        # restricted globals
        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "bool": bool,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "True": True,
                "False": False,
                "None": None
            }
        }
        
        # Add allowed modules
        for mod_name in self.allowed_modules:
            try:
                mod = __import__(mod_name)
                safe_globals[mod_name] = mod
            except ImportError:
                pass

        # Inject context variables
        safe_globals.update(context_variables)

        result = None
        success = False
        error_msg = ""

        try:
            with contextlib.redirect_stdout(stdout_capture):
                # We execute the code. The code is expected to define a function 'validate(scenario)' 
                # or just run and set a variable 'result'.
                # For Code-as-Policy, usually we expect a 'check()' function or similar.
                # Let's assume the code runs and we look for a 'result' variable or return value.
                exec(code, safe_globals)
                
                # Check if 'result' is in globals
                if 'result' in safe_globals:
                    result = safe_globals['result']
                    success = True
                else:
                    # If no result variable, maybe it was just a script.
                    success = True
                    
        except Exception as e:
            success = False
            error_msg = traceback.format_exc()

        return {
            "success": success,
            "result": result,
            "variables": safe_globals, # Return all variables to capture 'reason'
            "stdout": stdout_capture.getvalue(),
            "error": error_msg
        }

if __name__ == "__main__":
    # Test
    executor = SandboxExecutor()
    code = """
print("Checking compliance...")
if temperature > 38:
    result = False
else:
    result = True
"""
    ctx = {"temperature": 40}
    res = executor.execute(code, ctx)
    print(res)
