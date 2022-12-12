from dataclasses import dataclass
from typing import List, Dict

from game_src.dice_roll_mapping import DiceRollMapping
from game_src.game_configuration import GameConfiguration
from game_src.node_content import NodeContent


@dataclass
class GameNode:
    game_config: GameConfiguration
    node_id: str
    node_content: NodeContent
    option_to_dice_roll_mapping: Dict[str, DiceRollMapping] = None

    def __post_init__(self):
        if not self.option_to_dice_roll_mapping:
            self.option_to_dice_roll_mapping = {}
            for option_id, outcome_ids in self.node_content.option_to_outcome_mapping.items():
                dice_roll = DiceRollMapping(self.game_config, outcome_ids)
                self.option_to_dice_roll_mapping[option_id] = dice_roll

    def create_empty_child_nodes(self) -> List:
        if self.node_content.is_leaf:
            raise ValueError("Cannot expand a leaf into child nodes")

        child_depth = self.node_content.depth + 1
        child_is_leaf = child_depth == self.game_config.max_depth - 1
        id_prefix = self.node_id + f"_d{child_depth:02}"
        child_nodes = []
        for i, outcome_id in enumerate(self.node_content.get_outcome_id_list()):
            child_id = f"{id_prefix}n{i:02}"
            self.node_content.next_node_ids[outcome_id] = child_id
            child_content = NodeContent.create_with_empty_texts(self.game_config, child_id, child_is_leaf, child_depth)
            node = GameNode(self.game_config, child_id, child_content)
            child_nodes.append(node)
        return child_nodes

    def is_filled(self):
        return self.node_content.is_filled()

    @staticmethod
    def create_top_node(game_config: GameConfiguration):
        node_depth = 0
        node_id = f"d{node_depth:02}n00"
        content = NodeContent.create_with_empty_texts(game_config, node_id, False, node_depth)
        node = GameNode(game_config, node_id, content)
        return node

    def to_json(self):
        node_data = self.node_content.to_json_dict()
        return node_data

    @staticmethod
    def from_json(json_data, game_config: GameConfiguration):
        node_content = NodeContent.from_json_dict(json_data)
        return GameNode(game_config, node_content.node_id, node_content)




