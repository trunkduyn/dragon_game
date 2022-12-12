from typing import List

from game_src.game_configuration import GameConfiguration


class DiceRollMapping:

    def __init__(self, game_config: GameConfiguration, outcome_ids: List[str]):
        # check if number of responses suits the number of outcomes
        self.nr_dice_outcomes = game_config.nr_dice * 6
        assert self.nr_dice_outcomes % len(outcome_ids) == 0
        self.outcome_ids = outcome_ids
        self.dice_outcome_mapping = self.make_mapping()

    def check_dice_roll(self, dice_number):
        return self.dice_outcome_mapping[dice_number]

    def make_mapping(self):
        dice_mapping = {}
        for i in range(self.nr_dice_outcomes):
            response = self.outcome_ids[i % len(self.outcome_ids)]
            dice_mapping[i + 1] = response
        return dice_mapping
