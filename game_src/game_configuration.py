from dataclasses import dataclass, asdict


@dataclass
class GameConfiguration:
    nr_dice: int
    nr_answers: int
    nr_answer_outcomes: int
    max_depth: int

    @staticmethod
    def from_json_dict(json_config):
        return GameConfiguration(
            json_config['nr_dice'],
            json_config['nr_answers'],
            json_config['nr_answer_outcomes'],
            json_config['max_depth']
        )

    def to_json_dict(self):
        return asdict(self)
