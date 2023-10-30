from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, isfunction

from omegaconf import OmegaConf

resolvers_path = "resolvers/__init__.py"

resolver_spec = spec_from_file_location(name="resolvers", location=resolvers_path)

resolver_module = module_from_spec(resolver_spec)
resolver_spec.loader.exec_module(resolver_module)


for name, func in getmembers(resolver_module, isfunction):
    print("registered", name)
    OmegaConf.register_new_resolver(name, func, replace=True)

config = OmegaConf.create({"a": "${test2:}"})
OmegaConf.resolve(config)
print(config.a)
