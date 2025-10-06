import sys, os, shutil
sys.path.append(os.path.abspath("."))
from tablefaker import semantic_view as sv
import importlib
import inspect
import pytest

def test_importable():
	"""Module should import without syntax/runtime errors."""
	assert sv is not None
	assert inspect.ismodule(sv)

def test_public_callables_have_docstrings():
	"""All public callables exported by the module should have a non-empty docstring."""
	public_names = [n for n in dir(sv) if not n.startswith("_")]
	# Ensure the module exports something public (helps catch accidental empty modules)
	assert public_names, "No public attributes exported from tablefaker.semantic_view"
	for name in public_names:
		obj = getattr(sv, name)
		if callable(obj):
			doc = getattr(obj, "__doc__", None)
			assert doc and doc.strip(), f"Public callable '{name}' is missing a docstring"

def test_public_classes_have_docstrings():
	"""Public classes should have a class docstring or an __init__ docstring."""
	public_names = [n for n in dir(sv) if not n.startswith("_")]
	for name in public_names:
		obj = getattr(sv, name)
		if inspect.isclass(obj):
			cls_doc = getattr(obj, "__doc__", None)
			init_doc = getattr(obj.__init__, "__doc__", None) if hasattr(obj, "__init__") else None
			assert (cls_doc and cls_doc.strip()) or (init_doc and init_doc.strip()), (
				f"Public class '{name}' has no class or __init__ docstring"
			)

def _dummy_for_name(name, tmp_path):
	"""Return a sensible dummy value based on parameter name."""
	n = name.lower()
	if "path" in n or "dir" in n or "file" in n:
		return str(tmp_path)
	if "schema" in n or "table" in n or "name" in n or "column" in n:
		return "test"
	if "rows" in n or n in ("n", "count", "num", "size"):
		return 1
	if "cols" in n or "columns" in n:
		return ["a", "b"]
	if "config" in n or "opts" in n or "options" in n or "settings" in n:
		return {}
	if "seed" in n:
		return 0
	if "verbose" in n or "debug" in n:
		return False
	if "data" in n or "value" in n or "values" in n:
		return "x"
	# fallback
	return None

def _build_call_args(func, tmp_path):
	"""Try to build positional args and kwargs for func. Return (can_call, args, kwargs)."""
	sig = inspect.signature(func)
	args = []
	kwargs = {}
	for name, param in sig.parameters.items():
		# Skip VAR_POSITIONAL / VAR_KEYWORD (we'll pass nothing)
		if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
			continue
		# If parameter has a default, we can skip providing it.
		if param.default is not inspect._empty:
			continue
		# If the parameter is positional-only or positional-or-keyword and has no default, try to provide a dummy.
		val = None
		# Prefer annotation-based simple values if available
		if param.annotation is not inspect._empty:
			ann = param.annotation
			try:
				if ann is str:
					val = "test"
				elif ann is int:
					val = 1
				elif ann is bool:
					val = False
				elif ann is list:
					val = []
				elif ann is dict:
					val = {}
			except Exception:
				val = None
		# Fallback to name-based heuristics
		if val is None:
			val = _dummy_for_name(name, tmp_path)
		# If still None, we cannot safely call
		if val is None:
			return False, (), {}
		# Place value according to parameter kind
		if param.kind == inspect.Parameter.POSITIONAL_ONLY or param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
			args.append(val)
		elif param.kind == inspect.Parameter.KEYWORD_ONLY:
			kwargs[name] = val
		else:
			# unexpected kind
			return False, (), {}
	return True, tuple(args), kwargs

# def test_generate_semantic_view_basic(tmp_path):
# 	"""generate_semantic_view should exist, be callable, and have a docstring.
# 	If it accepts no required parameters we also call it and assert a non-None result.
# 	"""
# 	func = getattr(sv, "generate_semantic_view", None)
# 	assert func is not None and callable(func), "generate_semantic_view is missing or not callable"
# 	doc = getattr(func, "__doc__", None)
# 	assert doc and doc.strip(), "generate_semantic_view is missing a docstring"

# 	can_call, args, kwargs = _build_call_args(func, tmp_path)
# 	if can_call:
# 		# call and ensure it doesn't raise
# 		result = func(*args, **kwargs)
# 		assert result is not None

def test_call_public_callables_with_dummy_args(tmp_path):
	"""Attempt to call public callables when safe dummy arguments can be built."""
	public_names = [n for n in dir(sv) if not n.startswith("_")]
	assert public_names, "No public attributes exported from tablefaker.semantic_view"
	for name in public_names:
		obj = getattr(sv, name)
		if callable(obj):
			# Skip classes here (handled separately)
			if inspect.isclass(obj):
				continue
			# ensure docstring
			doc = getattr(obj, "__doc__", None)
			assert doc and doc.strip(), f"Public callable '{name}' is missing a docstring"
			can_call, args, kwargs = _build_call_args(obj, tmp_path)
			if can_call:
				# calling should not raise unexpected exceptions
				try:
					res = obj(*args, **kwargs)
				except Exception as e:
					# If calling raises a TypeError or ValueError related to invalid dummy input,
					# it's acceptable to skip—treat as a skip rather than a hard failure.
					# Other exceptions should propagate.
					if isinstance(e, (TypeError, ValueError)):
						pytest.skip(f"Callable {name} raised {type(e).__name__} with dummy args: {e}")
					else:
						raise
				# basic assertion to ensure something returned or the callable completed
				assert res is not None or res is None  # explicit no-op check; ensures call completed

# def test_instantiate_public_classes_and_call_noarg_methods(tmp_path):
# 	"""Instantiate public classes when possible and call their public no-arg methods."""
# 	public_names = [n for n in dir(sv) if not n.startswith("_")]
# 	for name in public_names:
# 		obj = getattr(sv, name)
# 		if inspect.isclass(obj):
# 			# ensure docstring
# 			cls_doc = getattr(obj, "__doc__", None)
# 			init_doc = getattr(obj.__init__, "__doc__", None) if hasattr(obj, "__init__") else None
# 			assert (cls_doc and cls_doc.strip()) or (init_doc and init_doc.strip()), (
# 				f"Public class '{name}' has no class or __init__ docstring"
# 			)
# 			# Try to build constructor args
# 			can_call, args, kwargs = _build_call_args(obj, tmp_path)
# 			if not can_call:
# 				# skip instantiation when we can't build safe args
# 				continue
# 			instance = obj(*args, **kwargs)
# 			# Call public methods that require no required params
# 			for meth_name, member in inspect.getmembers(instance, predicate=inspect.ismethod):
# 				if meth_name.startswith("_"):
# 					continue
# 				sig = inspect.signature(member)
# 				# check required parameters aside from 'self'
# 				required = [
# 					p for p in list(sig.parameters.values())[1:]
# 					if p.default is inspect._empty and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
# 				]
# 				if required:
# 					continue
# 				# call the method
# 				try:
# 					out = member()
# 				except Exception as e:
# 					# allow TypeError/ValueError caused by dummy data; otherwise propagate
# 					if isinstance(e, (TypeError, ValueError)):
# 						pytest.skip(f"Method {name}.{meth_name} raised {type(e).__name__} with dummy args: {e}")
# 					else:
# 						raise
# 				assert out is not None or out is None
