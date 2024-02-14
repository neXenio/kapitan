#!/usr/bin/env python3

# Copyright 2019 The Kapitan Authors
# SPDX-FileCopyrightText: 2020 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import multiprocessing as mp
import os
from copy import deepcopy
from dataclasses import dataclass, field
from time import time

import yaml
from omegaconf import ListMergeMode, OmegaConf, DictConfig

from kapitan import cached
from .migrate import migrate
from ..inventory import InventoryError, Inventory, InventoryTarget
from .resolvers import register_resolvers

logger = logging.getLogger(__name__)


class OmegaConfInventory(Inventory):
    classes_cache: dict = {}

    def render_targets(self, targets: list[InventoryTarget] = None, ignore_class_not_found: bool = False) -> None:

        targets = targets or self.targets.values()
        register_resolvers(self.inventory_path)

        # load targets parallel
        manager = mp.Manager()  # perf: bottleneck --> 90 % of the inventory time
        shared_targets = manager.dict()

        mp.set_start_method("spawn", True)  # platform independent
        with mp.Pool(min(len(targets), os.cpu_count())) as pool:
            r = pool.map_async(self.inventory_worker, [(self, target, shared_targets) for target in targets])
            r.wait()

        # store parameters and classes
        for target_name, rendered_target in rendered_inventory["nodes"].items():
            self.targets[target_name].parameters = rendered_target["parameters"]
            self.targets[target_name].classes = rendered_target["classes"]

    @staticmethod
    def inventory_worker(zipped_args):
        start = time()
        self, target, nodes = zipped_args

        try:
            register_resolvers(self.inventory_path)
            self.load_target(target)
            nodes[target.name] = {"parameters": target.parameters}
        except Exception as e:
            logger.error(f"{target.name}: {e}")
            return

        logger.info(f"Rendered {target.name} ({time()-start:.2f}s)")

    def migrate(self):
        migrate(self.inventory_path)

    def _load_target(self, target: InventoryTarget):
        """
        load only one target with all its classes
        """

        # load the target parameters
        target.classes, target.parameters = self._load_file(target.path)

        # load classes for targets
        for class_name in target.classes:
            inv_class = self._load_class(target, class_name)
            if not inv_class:
                # either redundantly defined or not found (with ignore_not_found: true)
                continue

            params = deepcopy(inv_class.parameters)
            target._merge(params)
            target.classes += inv_class.dependents

        if not target.parameters:
            # improve error msg
            raise InventoryError("empty target")

        # resolve interpolations
        target.add_metadata()
        target._resolve()

        # obtain target name to insert in inv dict
        vars_target_name = target.parameters.get("kapitan", {}).get("vars", {}).get("target")
        if not vars_target_name:
            # add hint to kapitan.vars.target
            logger.warning(f"Could not resolve target name on target {target.name}")

    def _load_class(self, target: InventoryTarget, class_name: str, ignore_class_not_found: bool = False):
        # resolve class path (has to be absolute)
        class_path = os.path.join(self.classes_path, *class_name.split("."))
        if class_name in target.classes:
            logger.debug(f"{class_path}: class {class_name} is redundantly defined")
            return None

        target.classes.append(class_name)

        # search in inventory classes cache, otherwise load class
        if class_name in self.classes_cache.keys():
            return self.classes_cache[class_name]

        # check if file exists
        if os.path.isfile(class_path + ".yml"):
            class_path += ".yml"
        elif os.path.isdir(class_path):
            # search for init file
            init_path = os.path.join(self.classes_path, *class_name.split("."), "init") + ".yml"
            if os.path.isfile(init_path):
                class_path = init_path
        elif ignore_class_notfound:
            logger.debug(f"Could not find {class_path}")
            return None
        else:
            raise InventoryError(f"Class {class_name} not found.")

        # load classes recursively
        classes, parameters = self._load_file(class_path)

        if not classes and not parameters:
            return None

        # resolve relative class names for new classes
        for c in classes:
            if c.startswith("."):
                c = ".".join(class_name.split(".")[0:-1]) + c
            inv_class.dependents.append(c)

        # add class to cache
        self.classes_cache[class_name] = inv_class

        return inv_class

    @staticmethod
    def _load_file(path: str):
        with open(path, "r") as f:
            f.seek(0)
            config = yaml.load(f, yaml.SafeLoader)

        if not config:
            return [], {}

        classes = OmegaConf.create(config.get("classes", []))
        parameters = OmegaConf.create(config.get("parameters", {}))

        # add metadata (filename, filepath) to node
        filename = os.path.splitext(os.path.split(path)[1])[0]
        parameters._set_flag(["filename", "path"], [filename, path], recursive=True)

        return classes, parameters

    @staticmethod
    def _merge_parameters(target_parameters: DictConfig, class_parameters: DictConfig) -> DictConfig:
        if not target_parameters:
            return class_parameters

        return OmegaConf.unsafe_merge(
            class_parameters, target_parameters, list_merge_mode=ListMergeMode.EXTEND,
        )

    @staticmethod
    def _resolve_parameters(target_parameters: DictConfig):
        # resolve first time
        OmegaConf.resolve(target_parameters, escape_interpolation_strings=False)

        # remove specified keys between first and second resolve-stage
        remove_location = "omegaconf.remove"
        removed_keys = OmegaConf.select(target_parameters, remove_location, default=[])
        for key in removed_keys:
            OmegaConf.update(target_parameters, key, {}, merge=False)

        # resolve second time and convert to object
        # TODO: add `throw_on_missing = True` when resolving second time (--> wait for to_object support)
        # reference: https://github.com/omry/omegaconf/pull/1113
        OmegaConf.resolve(target_parameters, escape_interpolation_strings=False)
        return OmegaConf.to_container(target_parameters)

    @staticmethod
    def _add_metadata(target: InventoryTarget):
        # append meta data (legacy: _reclass_)
        _kapitan_ = {
            "name": {
                "full": target.name,
                "parts": target.name.split("."),
                "path": target.name.replace(".", "/"),
                "short": target.name,
            }
        }
        target.parameters["_kapitan_"] = _kapitan_
        target.parameters["_reclass_"] = _kapitan_  # legacy
