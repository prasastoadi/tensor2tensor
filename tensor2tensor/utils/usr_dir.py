# coding=utf-8
# Copyright 2018 The Tensor2Tensor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility to load code from an external user-supplied directory."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import importlib
import os
import shutil
import sys
import tensorflow as tf
from collections import deque


INTERNAL_USR_DIR_PACKAGE = "t2t_usr_dir_internal"

def recursive_list(basedir):
    pathlist = deque()
    paths = tf.gfile.ListDirectory(basedir)
    pathlist.extend(paths)
    while len(pathlist):
        paths = []
        path = pathlist.popleft()
        fullpath = os.path.join(basedir,path)
        isdir = tf.gfile.IsDirectory(fullpath)
        if not isdir:
            yield path
        if isdir:
            paths = tf.gfile.ListDirectory(fullpath)
            paths = [path + p for p in paths]
        pathlist.extend(paths)
    return 

def recursive_copy(dir_path, tmp_dir):
    rec_list = recursive_list(dir_path)
    for path in rec_list:
        fullsrc = os.path.join(dir_path,path)
        fulldst = os.path.join(tmp_dir,path)
        tf.gfile.MakeDirs(os.path.dirname(fulldst))
        try:
            tf.gfile.Copy(fullsrc, fulldst)
        except:
            pass
    return 

def import_usr_dir(usr_dir):
  """Import module at usr_dir, if provided."""
  if not usr_dir or usr_dir=='None':
    return
  if usr_dir == INTERNAL_USR_DIR_PACKAGE:
    # The package has been installed with pip under this name for Cloud ML
    # Engine so just import it.
    importlib.import_module(INTERNAL_USR_DIR_PACKAGE)
    return

  dir_path = os.path.expanduser(usr_dir).rstrip("/")
  tmp_dir  = "/tmp/usr_dir"
  recursive_copy(dir_path, tmp_dir)
  containing_dir, module_name = os.path.split(tmp_dir)
  tf.logging.info("Importing user module %s from path %s", module_name,
                  containing_dir)
  sys.path.insert(0, containing_dir)
  importlib.import_module(module_name)
  sys.path.pop(0)
  shutil.rmtree(tmp_dir)
