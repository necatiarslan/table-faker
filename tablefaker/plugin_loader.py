# helper to enable loading custom python modules alongside config YAML files
import importlib
import importlib.machinery
import importlib.util
import sys
import os


def _load_spec(spec, extra_paths=()):
    """
    Load a Python module from either a module name or file path.

    Behavior:
      - If spec looks like a file path, load it directly from that path.
      - If spec is a module name and already loaded, reload it to pick up changes.
      - If spec is a module name and not loaded, import it normally.
    """
    for p in extra_paths:
        if p and p not in sys.path:
            sys.path.insert(0, p)

    # Allow plain module names or file paths
    if spec.endswith(".py") or os.sep in spec or spec.startswith("."):
        # Load from file path (always re-executes the file)
        mod_name = os.path.splitext(os.path.basename(spec))[0]
        path = os.path.abspath(spec)
        loader = importlib.machinery.SourceFileLoader(mod_name, path)
        mod = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(mod_name, loader)
        )
        loader.exec_module(mod)
        return mod

    # Load from module name. If already loaded, reload to pick up edits.
    try:
        if spec in sys.modules:
            return importlib.reload(sys.modules[spec])
        return importlib.import_module(spec)
    except Exception:
        # Fallback: attempt a fresh import as last resort
        return importlib.import_module(spec)


def tf_expose(fn=None, *, name=None):
    """
    Decorator to expose a function to the TableFaker evaluation environment.
    
    Usage:
        @tf_expose()
        def my_function():
            pass
        
        @tf_expose(name="custom_name")
        def my_function():
            pass
    
    Args:
        fn: The function to decorate (when used without parentheses)
        name: Optional custom name for the function in the eval environment
    
    Returns:
        The decorated function with metadata attributes
    """
    def wrap(f):
        setattr(f, "__tf_exported__", True)
        setattr(f, "__tf_export_name__", name or f.__name__)
        return f
    
    return wrap if fn is None else wrap(fn)


class PluginManager:
    """
    Manages loading and exposing custom Python modules/functions to TableFaker.
    
    This allows users to place custom helper modules alongside their config YAML
    files and reference them in data expressions.
    """
    
    def __init__(self, module_specs, extra_paths=()):
        """
        Initialize the plugin manager and load specified modules.
        
        Args:
            module_specs: List of module names or file paths to load
            extra_paths: Additional paths to search for modules
        """
        self.modules = []
        self.exports = {}  # flat functions exposed by @tf_expose
        
        for spec in module_specs or []:
            try:
                m = _load_spec(spec, extra_paths)
                self.modules.append(m)
                
                # Scan for functions decorated with @tf_expose
                for attr in dir(m):
                    obj = getattr(m, attr)
                    if callable(obj) and getattr(obj, "__tf_exported__", False):
                        export_name = getattr(obj, "__tf_export_name__")
                        self.exports[export_name] = obj
            except Exception as e:
                # Log but don't fail - allows optional plugins
                import warnings
                warnings.warn(f"Failed to load plugin '{spec}': {e}")
    
    def make_eval_locals(self, base_locals, get_table):
        """
        Create the evaluation environment with base locals plus plugin exports.
        
        Args:
            base_locals: Base dictionary of variables (fake, random, etc.)
            get_table: Function to retrieve generated table data
        
        Returns:
            Dictionary to use as locals in eval/exec calls
        """
        env = dict(base_locals)
        
        # Add module aliases (use bare module name in YAML)
        for m in self.modules:
            module_name = m.__name__.split(".")[-1]
            env[module_name] = m
        
        # Add flat exposed functions (decorated with @tf_expose)
        env.update(self.exports)
        
        # Add utility function to access other tables
        env["get_table"] = get_table
        
        return env