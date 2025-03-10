# Copyright 2020 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Base class for wrappers."""

from meltingpot.python import substrate

Substrate = substrate.Substrate


class Wrapper(substrate.Substrate):
  """Base class for Substrate wrappers."""

  def __init__(self, env: substrate.Substrate):
    """Initializer.

    Args:
      env: An environment to wrap. This environment will be closed with this
        wrapper.
    """
    # pylint: disable=useless-super-delegation
    super().__init__(env)
