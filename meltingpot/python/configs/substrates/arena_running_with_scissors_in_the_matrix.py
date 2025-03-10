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
"""Configuration for Arena Running with Scissors in the Matrix.

Example video: https://youtu.be/esXPyGBIf2Y

This substrate is the same as _Running with Scissors in the Matrix_ except in
this case there are eight players and the map layout is different. Even though
there are eight players, they still interact in dyadic pairs via the usual
rock-paper-scissors payoff matrix.

Players have the default `11 x 11` (off center) observation window.
"""

import copy
from typing import Any, Dict, Iterable, Sequence, Tuple

from ml_collections import config_dict
from meltingpot.python.utils.substrates import colors
from meltingpot.python.utils.substrates import game_object_utils
from meltingpot.python.utils.substrates import shapes

PrefabConfig = game_object_utils.PrefabConfig

# The number of resources must match the (square) size of the matrix.
NUM_RESOURCES = 3

# This color is yellow.
RESOURCE1_COLOR = (255, 227, 11, 255)
RESOURCE1_HIGHLIGHT_COLOR = (255, 214, 91, 255)
RESOURCE1_COLOR_DATA = (RESOURCE1_COLOR, RESOURCE1_HIGHLIGHT_COLOR)
# This color is violet.
RESOURCE2_COLOR = (109, 42, 255, 255)
RESOURCE2_HIGHLIGHT_COLOR = (132, 91, 255, 255)
RESOURCE2_COLOR_DATA = (RESOURCE2_COLOR, RESOURCE2_HIGHLIGHT_COLOR)
# This color is cyan.
RESOURCE3_COLOR = (42, 188, 255, 255)
RESOURCE3_HIGHLIGHT_COLOR = (91, 214, 255, 255)
RESOURCE3_COLOR_DATA = (RESOURCE3_COLOR, RESOURCE3_HIGHLIGHT_COLOR)

# The procedural generator replaces all 'a' chars in the default map with chars
# representing specific resources, i.e. with either '1' or '2'.
DEFAULT_ASCII_MAP = """
WWWWWWWWWWWWWWWWWWWWWWWWW
WPPPP      W W      PPPPW
WPPPP               PPPPW
WPPPP               PPPPW
WPPPP               PPPPW
W             aa        W
W        11   aa        W
W        11             W
W        11             W
W    WW     W  222      W
WW    33    W  222      W
WWW   33  WWWWWWWWW     W
W     33    111       WWW
W           111         W
W       22 W            W
W       22 W   WW       W
W       22     W333     W
W               333     W
W          aa           W
WPPPP      aa       PPPPW
WPPPP               PPPPW
WPPPP               PPPPW
WPPPP         W     PPPPW
WWWWWWWWWWWWWWWWWWWWWWWWW
"""

_resource_names = [
    "resource_class1",
    "resource_class2",
    "resource_class3",
]

# `prefab` determines which prefab game object to use for each `char` in the
# ascii map.
CHAR_PREFAB_MAP = {
    "a": {"type": "choice", "list": _resource_names},
    "1": _resource_names[0],
    "2": _resource_names[1],
    "3": _resource_names[2],
    "P": "spawn_point",
    "W": "wall",
}

_COMPASS = ["N", "E", "S", "W"]

WALL = {
    "name": "wall",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "wall",
                "stateConfigs": [{
                    "state": "wall",
                    "layer": "upperPhysical",
                    "sprite": "Wall",
                }],
            }
        },
        {
            "component": "Transform",
            "kwargs": {
                "position": (0, 0),
                "orientation": "N"
            }
        },
        {
            "component": "Appearance",
            "kwargs": {
                "renderMode": "ascii_shape",
                "spriteNames": ["Wall"],
                "spriteShapes": [shapes.WALL],
                "palettes": [{"*": (95, 95, 95, 255),
                              "&": (100, 100, 100, 255),
                              "@": (109, 109, 109, 255),
                              "#": (152, 152, 152, 255)}],
                "noRotates": [False]
            }
        },
        {
            "component": "BeamBlocker",
            "kwargs": {
                "beamType": "gameInteraction"
            }
        },
    ]
}

SPAWN_POINT = {
    "name": "spawnPoint",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "spawnPoint",
                "stateConfigs": [{
                    "state": "spawnPoint",
                    "layer": "alternateLogic",
                    "groups": ["spawnPoints"]
                }],
            }
        },
        {
            "component": "Transform",
            "kwargs": {
                "position": (0, 0),
                "orientation": "N"
            }
        },
    ]
}

# PLAYER_COLOR_PALETTES is a list with each entry specifying the color to use
# for the player at the corresponding index.
NUM_PLAYERS_UPPER_BOUND = 32
PLAYER_COLOR_PALETTES = []
for idx in range(NUM_PLAYERS_UPPER_BOUND):
  PLAYER_COLOR_PALETTES.append(shapes.get_palette(colors.palette[idx]))

# Primitive action components.
# pylint: disable=bad-whitespace
# pyformat: disable
NOOP       = {"move": 0, "turn":  0, "interact": 0}
FORWARD    = {"move": 1, "turn":  0, "interact": 0}
STEP_RIGHT = {"move": 2, "turn":  0, "interact": 0}
BACKWARD   = {"move": 3, "turn":  0, "interact": 0}
STEP_LEFT  = {"move": 4, "turn":  0, "interact": 0}
TURN_LEFT  = {"move": 0, "turn": -1, "interact": 0}
TURN_RIGHT = {"move": 0, "turn":  1, "interact": 0}
INTERACT   = {"move": 0, "turn":  0, "interact": 1}
# pyformat: enable
# pylint: enable=bad-whitespace

ACTION_SET = (
    NOOP,
    FORWARD,
    BACKWARD,
    STEP_LEFT,
    STEP_RIGHT,
    TURN_LEFT,
    TURN_RIGHT,
    INTERACT,
)

TARGET_SPRITE_SELF = {
    "name": "Self",
    "shape": shapes.CUTE_AVATAR,
    "palette": shapes.get_palette((50, 100, 200)),
    "noRotate": True,
}


def create_scene():
  """Creates the global scene."""
  scene = {
      "name": "scene",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": "scene",
                  "stateConfigs": [{
                      "state": "scene",
                  }],
              }
          },
          {
              "component": "Transform",
              "kwargs": {
                  "position": (0, 0),
                  "orientation": "N"
              },
          },
          {
              "component": "TheMatrix",
              "kwargs": {
                  "zero_initial_inventory": False,
                  "matrix": [
                      [0, -1, 1],
                      [1, 0, -1],
                      [-1, 1, 0]
                  ],
              }
          },
      ]
  }
  return scene


def create_resource_prefab(resource_id, color_data):
  """Creates resource prefab with provided `resource_id` (num) and color."""
  resource_name = "resource_class{}".format(resource_id)
  resource_prefab = {
      "name": resource_name,
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": resource_name,
                  "stateConfigs": [
                      {"state": resource_name + "_wait",
                       "groups": ["resourceWaits"]},
                      {"state": resource_name,
                       "layer": "lowerPhysical",
                       "sprite": resource_name + "_sprite"},
                  ]
              },
          },
          {
              "component": "Transform",
              "kwargs": {
                  "position": (0, 0),
                  "orientation": "N"
              },
          },
          {
              "component": "Appearance",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "spriteNames": [resource_name + "_sprite"],
                  "spriteShapes": [shapes.BUTTON],
                  "palettes": [{"*": color_data[0],
                                "#": color_data[1],
                                "x": (0, 0, 0, 0)}],
                  "noRotates": [False]
              },
          },
          {
              "component": "Resource",
              "kwargs": {
                  "resourceClass": resource_id,
                  "visibleType": resource_name,
                  "waitState": resource_name + "_wait",
                  "groupToRespawn": "resourceWaits",
                  "regenerationRate": 0.005,
                  "regenerationDelay": 50
              },
          },
          {
              "component": "Destroyable",
              "kwargs": {
                  "visibleType": resource_name,
                  "waitState": resource_name + "_wait",
                  "initialHealth": 1,
              },
          },
      ]
  }
  return resource_prefab


def create_prefabs() -> PrefabConfig:
  """Returns the prefabs.

  Prefabs are a dictionary mapping names to template game objects that can
  be cloned and placed in multiple locations accoring to an ascii map.
  """
  prefabs = {
      "wall": WALL,
      "spawn_point": SPAWN_POINT,
  }
  prefabs["resource_class1"] = create_resource_prefab(1, RESOURCE1_COLOR_DATA)
  prefabs["resource_class2"] = create_resource_prefab(2, RESOURCE2_COLOR_DATA)
  prefabs["resource_class3"] = create_resource_prefab(3, RESOURCE3_COLOR_DATA)
  return prefabs


def create_avatar_object(player_idx: int,
                         target_sprite_self: Dict[str, Any]) -> Dict[str, Any]:
  """Create an avatar object that always sees itself as blue."""
  # Lua is 1-indexed.
  lua_index = player_idx + 1

  # Setup the self vs other sprite mapping.
  source_sprite_self = "Avatar" + str(lua_index)
  custom_sprite_map = {source_sprite_self: target_sprite_self["name"]}

  live_state_name = "player{}".format(lua_index)
  avatar_object = {
      "name": "avatar",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": live_state_name,
                  "stateConfigs": [
                      {"state": live_state_name,
                       "layer": "upperPhysical",
                       "sprite": source_sprite_self,
                       "contact": "avatar",
                       "groups": ["players"]},

                      {"state": "playerWait",
                       "groups": ["playerWaits"]},
                  ]
              }
          },
          {
              "component": "Transform",
              "kwargs": {
                  "position": (0, 0),
                  "orientation": "N"
              }
          },
          {
              "component": "Appearance",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "spriteNames": [source_sprite_self],
                  "spriteShapes": [shapes.CUTE_AVATAR],
                  "palettes": [shapes.get_palette(colors.palette[player_idx])],
                  "noRotates": [True]
              }
          },
          {
              "component": "AdditionalSprites",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "customSpriteNames": [target_sprite_self["name"]],
                  "customSpriteShapes": [target_sprite_self["shape"]],
                  "customPalettes": [target_sprite_self["palette"]],
                  "customNoRotates": [target_sprite_self["noRotate"]],
              }
          },
          {
              "component": "Avatar",
              "kwargs": {
                  "index": lua_index,
                  "aliveState": live_state_name,
                  "waitState": "playerWait",
                  "speed": 1.0,
                  "spawnGroup": "spawnPoints",
                  "actionOrder": ["move", "turn", "interact"],
                  "actionSpec": {
                      "move": {"default": 0, "min": 0, "max": len(_COMPASS)},
                      "turn": {"default": 0, "min": -1, "max": 1},
                      "interact": {"default": 0, "min": 0, "max": 1},
                  },
                  "view": {
                      "left": 5,
                      "right": 5,
                      "forward": 9,
                      "backward": 1,
                      "centered": False
                  },
                  "spriteMap": custom_sprite_map,
                  # The following kwarg makes it possible to get rewarded even
                  # on frames when an avatar is "dead". It is needed for in the
                  # matrix games in order to correctly handle the case of two
                  # players getting hit simultaneously by the same beam.
                  "skipWaitStateRewards": False,
              }
          },
          {
              "component": "GameInteractionZapper",
              "kwargs": {
                  "cooldownTime": 2,
                  "beamLength": 3,
                  "beamRadius": 1,
                  "framesTillRespawn": 200,
                  "numResources": NUM_RESOURCES,
                  "reset_winner_inventory": False,
                  "reset_loser_inventory": True,
                  "losingPlayerDies": True,
              }
          },
          {
              "component": "ReadyToShootObservation",
              "kwargs": {
                  "zapperComponent": "GameInteractionZapper",
              }
          },
          {
              "component": "InventoryObserver",
              "kwargs": {
              }
          },
          {
              "component": "Taste",
              "kwargs": {
                  "mostTastyResourceClass": -1,  # -1 indicates no preference.
                  "mostTastyReward": 1.0,  # reward for most tasty.
                  "defaultTastinessReward": 0.0,  # reward for others.
              }
          },
          {
              "component": "InteractionTaste",
              "kwargs": {
                  "mostTastyResourceClass": -1,  # -1 indicates no preference.
                  "zeroDefaultInteractionReward": False,
                  "extraReward": 1.0,
              }
          },
          {
              "component": "LocationObserver",
              "kwargs": {
                  "objectIsAvatar": True,
                  "alsoReportOrientation": True
              }
          },
          {
              "component": "AvatarMetricReporter",
              "kwargs": {
                  "metrics": [
                      {
                          # Report the inventories of both players involved in
                          # an interaction on this frame formatted as
                          # (self inventory, partner inventory).
                          "name": "INTERACTION_INVENTORIES",
                          "type": "tensor.DoubleTensor",
                          "shape": (2, NUM_RESOURCES),
                          "component": "GameInteractionZapper",
                          "variable": "latest_interaction_inventories",
                      },
                  ]
              }
          },
      ]
  }

  return avatar_object


def create_avatar_objects(num_players: int) -> Sequence[PrefabConfig]:
  """Returns all game objects for the map.

  Args:
    num_players: number of players to create avatars for.
  """
  avatar_objects = []
  for player_idx in range(num_players):
    avatar = create_avatar_object(player_idx, TARGET_SPRITE_SELF)
    avatar_objects.append(avatar)
  return avatar_objects


def create_lab2d_settings(
    num_players: int,
    ascii_map_string: str,
    settings_overrides: Iterable[Tuple[str, Any]] = ()) -> Dict[str, Any]:
  """Returns the lab2d settings.

  Args:
    num_players: (int) the number of players.
    ascii_map_string: ascii map.
    settings_overrides: (key, value) overrides for default settings.
  """
  settings = {
      "levelName": "the_matrix",
      "levelDirectory": "meltingpot/lua/levels",
      "numPlayers": num_players,
      "episodeLengthFrames": 1000,
      "spriteSize": 8,
      "simulation": {
          "map": ascii_map_string,
          "gameObjects": create_avatar_objects(num_players=num_players),
          "scene": copy.deepcopy(create_scene()),
          "prefabs": create_prefabs(),
          "charPrefabMap": CHAR_PREFAB_MAP,
      }
  }
  settings.update(settings_overrides)
  return settings


def get_config(factory=create_lab2d_settings):
  """Default config for running with scissors arena in the matrix."""
  config = config_dict.ConfigDict()

  # Basic configuration.
  config.num_players = 8

  # Lua script configuration.
  config.lab2d_settings = factory(config.num_players, DEFAULT_ASCII_MAP)

  # Action set configuration.
  config.action_set = ACTION_SET
  # Observation format configuration.
  config.individual_observation_names = [
      "RGB",
      "INVENTORY",
      "READY_TO_SHOOT",
      "POSITION",
      "ORIENTATION",
      "INTERACTION_INVENTORIES",
  ]
  config.global_observation_names = [
      "WORLD.RGB",
  ]

  return config
