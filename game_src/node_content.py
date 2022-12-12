from dataclasses import dataclass, fields, asdict
from typing import Dict, List

from game_src.game_configuration import GameConfiguration


@dataclass
class NodeContent:
    node_id: str
    is_leaf: bool
    depth: int
    situation_description: str = ""
    option_texts: Dict[str, str] = None
    option_to_outcome_mapping: Dict[str, List[str]] = None
    final_outcome_texts: Dict[str, str] = None
    next_node_ids: Dict[str, str] = None

    def __post_init__(self):
        # not both values can be filled
        leaf_node_or_pointer = not (self.final_outcome_texts is not None and self.next_node_ids is not None)
        assert leaf_node_or_pointer

    def is_filled(self):
        if not self.situation_description:
            return False
        if not self.option_texts:
            return False
        if self.is_leaf and not self.final_outcome_texts:
            return False
        if not all(self.option_texts.values()):
            return False
        if self.is_leaf and not all(self.final_outcome_texts.values()):
            return False
        return True

    def get_nr_outcomes(self) -> int:
        return len(self.final_outcome_texts) if self.is_leaf else len(self.next_node_ids)

    def get_outcome_id_list(self) -> List[str]:
        if self.is_leaf:
            sorted(self.final_outcome_texts.keys())
        return sorted(self.next_node_ids.keys())

    @staticmethod
    def create_with_empty_texts(game_config: GameConfiguration, node_id: str, is_leaf: bool, depth: int):
        option_texts = {}
        options_to_output_mapping = {}
        outcomes = {}
        for i in range(game_config.nr_answers):
            option_id = f"{node_id}_OPT{i:02}"
            option_texts[option_id] = ""
            options_to_output_mapping[option_id] = []
            for outcome_nr in range(game_config.nr_answer_outcomes):
                outcome_id = f"{option_id}_OUT{outcome_nr:02}"
                outcomes[outcome_id] = ""
                options_to_output_mapping[option_id].append(outcome_id)

        args = [node_id, is_leaf, depth, "", option_texts, options_to_output_mapping]
        if is_leaf:
            return NodeContent(*args, final_outcome_texts=outcomes)

        return NodeContent(*args,  next_node_ids=outcomes)

    def to_json_dict(self):
        if self.node_id == "d00n00":
            x=2
        return asdict(self)

    def to_json_dict2(self):
        node_data = {
            "node_id": self.node_id,
            "is_leaf": self.is_leaf,
            "depth": self.depth,
            "situation_description": self.situation_description,
            "option_texts": self.option_texts,
            "final_outcome_texts": self.final_outcome_texts,
            "next_node_ids": self.next_node_ids,
            "option_to_outcome_mapping": self.option_to_outcome_mapping,
        }
        return node_data

    @classmethod
    def from_json_dict(cls, arg_dict):
        field_set = {f.name for f in fields(cls) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return cls(**filtered_arg_dict)

