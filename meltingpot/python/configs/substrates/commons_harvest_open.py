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
"""Configuration for Commons Harvest: Open.

Example video: https://youtu.be/ZwQaUj8GS6U

Apples are spread around the map and can be consumed for a reward of 1. Apples
that have been consumed regrow with a per-step probability that depends on the
number of uneaten apples in a `L2` norm neighborhood of radius 2 (by default).
After an apple has been eaten and thus removed, its regrowth probability depends
on the number of uneaten apples still in its local neighborhood. With standard
parameters, it the grown rate decreases as the number of uneaten apples in the
neighborhood decreases and when there are zero uneaten apples in the
neighborhood then the regrowth rate is zero. As a consequence, a patch of apples
that collectively doesn't have any nearby apples, can be irrevocably lost if all
apples in the patch are consumed. Therefore, agents must exercise restraint when
consuming apples within a patch. Notice that in a single agent situation, there
is no incentive to collect the last apple in a patch (except near the end of the
episode). However, in a multi-agent situation, there is an incentive for any
agent to consume the last apple rather than risk another agent consuming it.
This creates a tragedy of the commons from which the substrate derives its name.

This mechanism was first described in Janssen et al (2010) and adapted for
multi-agent reinforcement learning in Perolat et al (2017).

Janssen, M.A., Holahan, R., Lee, A. and Ostrom, E., 2010. Lab experiments for
the study of social-ecological systems. Science, 328(5978), pp.613-617.

Perolat, J., Leibo, J.Z., Zambaldi, V., Beattie, C., Tuyls, K. and Graepel, T.,
2017. A multi-agent reinforcement learning model of common-pool
resource appropriation. In Proceedings of the 31st International Conference on
Neural Information Processing Systems (pp. 3646-3655).
"""

from typing import Any, Dict

from ml_collections import config_dict
import numpy as np

from meltingpot.python.utils.substrates import colors
from meltingpot.python.utils.substrates import shapes


APPLE_RESPAWN_RADIUS = 2.0
REGROWTH_PROBABILITIES = [0.0, 0.0025, 0.005, 0.025]

ASCII_MAP = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
W                         PPPP                          W
W   A                                               A   W
W  AAA            PPPP            PPPP             AAA  W
W AAAAA                                           AAAAA W
W  AAA                                             AAA  W
W   A         A        A                            A   W
WP           AAA      AAA       A        A             PW
WP  A   A A AAAA A A AAAAAA A  AAA      AAA         A  PW
WP           AAA      AAA   A AAAAA A A AAAA A A       PW
WP  A   A     A        A       AAA      AAA         A  PW
WP     AA                       A        A     AA      PW
WP  A AAA              A                       AAA AA  PW
WP     AA                       A              AA      PW
WP  A   A              A                       A    A  PW
WP                              A                      PW
WP  A       PPPPPPPPPPPAPPPPPPPPPPPPPPPPPPPP        A  PW
WP                              A                      PW
WP  A                  A                            A  PW
WP AAA                          A        A         AAA PW
WPAAAAA       A        A       AAA      AAA       AAAAAPW
WP AAA       AAA      AAA   A AAAAA A A AAAA A A A AAA PW
WP  A   A A AAAA A A AAAAAA A  AAA      AAA         A  PW
WP           AAA      AAA       A        A   A         PW
W   A   A     A        A                                W
W                                            A          W
W   A   A                                      A        W
W      AA         PPPP            PPPP       A AA       W
W   A AAA                                      AAA      W
W                         PPPP                          W
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
"""

# `prefab` determines which prefab game object to use for each `char` in the
# ascii map.
CHAR_PREFAB_MAP = {
    "P": "spawn_point",
    "W": "wall",
    "A": "apple",
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
                "beamType": "zapHit"
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

# Primitive action components.
# pylint: disable=bad-whitespace
# pyformat: disable
NOOP       = {"move": 0, "turn":  0, "fireZap": 0}
FORWARD    = {"move": 1, "turn":  0, "fireZap": 0}
STEP_RIGHT = {"move": 2, "turn":  0, "fireZap": 0}
BACKWARD   = {"move": 3, "turn":  0, "fireZap": 0}
STEP_LEFT  = {"move": 4, "turn":  0, "fireZap": 0}
TURN_LEFT  = {"move": 0, "turn": -1, "fireZap": 0}
TURN_RIGHT = {"move": 0, "turn":  1, "fireZap": 0}
FIRE_ZAP   = {"move": 0, "turn":  0, "fireZap": 1}
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
    FIRE_ZAP,
)

TARGET_SPRITE_SELF = {
    "name": "Self",
    "shape": shapes.CUTE_AVATAR,
    "palette": shapes.get_palette((50, 100, 200)),
    "noRotate": True,
}


def create_scene():
  """Creates the scene with the provided args controlling apple regrowth."""
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
              "component": "Neighborhoods",
              "kwargs": {}
          },
      ]
  }

  return scene


def create_apple_prefab(regrowth_radius=-1.0,  # pylint: disable=dangerous-default-value
                        regrowth_probabilities=[0, 0.0, 0.0, 0.0]):
  """Creates the apple prefab with the provided settings."""
  growth_rate_states = [
      {
          "state": "apple",
          "layer": "lowerPhysical",
          "sprite": "Apple",
          "groups": ["apples"]
      },
      {
          "state": "appleWait",
          "layer": "logic",
          "sprite": "AppleWait",
      },
  ]
  # Enumerate all possible states for a potential apple. There is one state for
  # each regrowth rate i.e., number of nearby apples.
  upper_bound_possible_neighbors = np.floor(np.pi*regrowth_radius**2+1)+1
  for i in range(int(upper_bound_possible_neighbors)):
    growth_rate_states.append(dict(state="appleWait_{}".format(i),
                                   layer="logic",
                                   groups=["waits_{}".format(i)],
                                   sprite="AppleWait"))

  apple_prefab = {
      "name": "apple",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": "apple",
                  "stateConfigs": growth_rate_states,
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
                  "spriteNames": ["Apple", "AppleWait"],
                  "spriteShapes": [shapes.APPLE, shapes.APPLE],
                  "palettes": [{"*": (102, 255, 0, 255),
                                "@": (230, 255, 0, 255),
                                "&": (117, 255, 26, 255),
                                "#": (255, 153, 0, 255),
                                "x": (0, 0, 0, 0)},
                               {"*": (102, 255, 0, 25),
                                "@": (230, 255, 0, 25),
                                "&": (117, 255, 26, 25),
                                "#": (255, 153, 0, 25),
                                "x": (0, 0, 0, 0)}],
                  "noRotates": [False, False]
              }
          },
          {
              "component": "Edible",
              "kwargs": {
                  "liveState": "apple",
                  "waitState": "appleWait",
                  "rewardForEating": 1.0,
              }
          },
          {
              "component": "DensityRegrow",
              "kwargs": {
                  "liveState": "apple",
                  "waitState": "appleWait",
                  "radius": regrowth_radius,
                  "regrowthProbabilities": regrowth_probabilities,
              }
          },
      ]
  }

  return apple_prefab


def create_prefabs(regrowth_radius=-1.0,
                   # pylint: disable=dangerous-default-value
                   regrowth_probabilities=[0, 0.0, 0.0, 0.0]):
  """Returns a dictionary mapping names to template game objects."""
  prefabs = {
      "wall": WALL,
      "spawn_point": SPAWN_POINT,
  }
  prefabs["apple"] = create_apple_prefab(
      regrowth_radius=regrowth_radius,
      regrowth_probabilities=regrowth_probabilities)
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
                  "actionOrder": ["move", "turn", "fireZap"],
                  "actionSpec": {
                      "move": {"default": 0, "min": 0, "max": len(_COMPASS)},
                      "turn": {"default": 0, "min": -1, "max": 1},
                      "fireZap": {"default": 0, "min": 0, "max": 1},
                  },
                  "view": {
                      "left": 5,
                      "right": 5,
                      "forward": 9,
                      "backward": 1,
                      "centered": False
                  },
                  "spriteMap": custom_sprite_map,
              }
          },
          {
              "component": "Zapper",
              "kwargs": {
                  "cooldownTime": 2,
                  "beamLength": 3,
                  "beamRadius": 1,
                  "framesTillRespawn": 4,
                  "penaltyForBeingZapped": 0,
                  "rewardForZapping": 0,
              }
          },
          {
              "component": "ReadyToShootObservation",
          },
          {
              "component": "LocationObserver",
              "kwargs": {
                  "objectIsAvatar": True,
                  "alsoReportOrientation": True
              }
          },
      ]
  }
  return avatar_object


def create_avatar_objects(num_players):
  """Returns list of avatar objects of length 'num_players'."""
  avatar_objects = []
  for player_idx in range(0, num_players):
    game_object = create_avatar_object(player_idx,
                                       TARGET_SPRITE_SELF)
    avatar_objects.append(game_object)

  return avatar_objects


def create_lab2d_settings(num_players: int) -> Dict[str, Any]:
  """Returns the lab2d settings."""
  lab2d_settings = {
      "levelName": "commons_harvest",
      "levelDirectory":
          "meltingpot/lua/levels",
      "numPlayers": num_players,
      "episodeLengthFrames": 1000,
      "spriteSize": 8,
      "simulation": {
          "map": ASCII_MAP,
          "gameObjects": create_avatar_objects(num_players),
          "prefabs": create_prefabs(APPLE_RESPAWN_RADIUS,
                                    REGROWTH_PROBABILITIES),
          "charPrefabMap": CHAR_PREFAB_MAP,
          "scene": create_scene(),
      },
  }
  return lab2d_settings


def get_config():
  """Default configuration for training on the commons_harvest level."""
  config = config_dict.ConfigDict()

  # Basic configuration.
  config.num_players = 16

  # Lua script configuration.
  config.lab2d_settings = create_lab2d_settings(config.num_players)

  # Action set configuration.
  config.action_set = ACTION_SET
  # Observation format configuration.
  config.individual_observation_names = [
      "RGB",
      "READY_TO_SHOOT",
      "POSITION",
      "ORIENTATION",
  ]
  config.global_observation_names = [
      "WORLD.RGB",
  ]

  return config
