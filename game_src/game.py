import json
from typing import Dict, Tuple, List

from game_src.game_configuration import GameConfiguration
from game_src.game_node import GameNode


def ask_next_game():
    user_response = input("\n\nwant to play another round? y/n")
    if user_response == 'n':
        return False
    return True


class Game:

    def __init__(self, top_node: GameNode, node_mapping: Dict[str, GameNode]):
        self.top_node = top_node
        self.node_mapping = node_mapping
        self.nr_leaves = sum(1 for n in self.node_mapping.values() if n.node_content.is_leaf)

    def play(self):
        user_continues = True

        while user_continues:
            node = self.top_node
            leave_reached = False
            while not leave_reached:
                print("\n\n\n"+"="*15)
                print(node.node_content.situation_description)
                # ask which action player wants to take
                cur_options = {}
                print("\nwhich action do you want to take?")
                for i, option_id in enumerate(node.node_content.option_texts.keys()):
                    text = node.node_content.option_texts[option_id]
                    print(f"{i}) {text}")
                    cur_options[i] = option_id

                result = input("Press the number:\n")
                option_id = cur_options[int(result)]

                # ask what the player rolled with the dice
                result = int(input("what did you roll?\n"))
                outcome_id = node.option_to_dice_roll_mapping[option_id].check_dice_roll(result)

                if node.node_content.is_leaf:
                    final_outcome = node.node_content.final_outcome_texts[outcome_id]
                    print(f"OUTCOME:\n{final_outcome}")
                    leave_reached = True
                else:
                    outcome = node.node_content.next_node_ids[outcome_id]
                    node = self.node_mapping[outcome]

            user_continues = ask_next_game()

    def traverse_depth_first_and_yield_empty_texts(self) -> Tuple[GameNode, List[str]]:
        """
        Travers through the game graph depth first and yield any node that
        travers depth first because then you add story line by story line which is less confusing
        :return:
        """
        assert all(node.node_id==node_id for node_id, node in self.node_mapping.items())
        next_nodes = []
        current_state = [self.top_node, []]
        node_nr = 0

        while current_state is not None:
            current_node, current_story = current_state
            if not current_node.is_filled():
                yield current_node, current_story, node_nr

            current_content = current_node.node_content
            current_story.append(current_content.situation_description)

            for answer_id, outcome_ids in current_content.option_to_outcome_mapping.items():
                answer = current_content.option_texts[answer_id]
                for outcome_id in outcome_ids:
                    # add next nodes to list of states for checking
                    if not current_content.is_leaf:
                        next_node_id = current_content.next_node_ids[outcome_id]
                        outcome_story = current_story + [answer]
                        next_nodes.append((self.node_mapping[next_node_id], outcome_story))

            current_state = next_nodes.pop() if next_nodes else None
            node_nr += 1

    @staticmethod
    def new_game_creation(game_config: GameConfiguration):
        game_config = game_config
        top_node = GameNode.create_top_node(game_config)
        current_nodes = [top_node]
        next_nodes = []
        all_nodes = {top_node.node_id: top_node}

        print(f"start with node {top_node.node_id}")
        # depth -1 because already created depth 1 -> top node
        for i in range(game_config.max_depth - 1):
            print(f"Expanding depth {i}, Containing {len(current_nodes)} nodes")
            for node in current_nodes:
                child_nodes = node.create_empty_child_nodes()
                for child_node in child_nodes:
                    print(f"created node {child_node.node_id}")
                    all_nodes[child_node.node_id] = child_node
                next_nodes.extend(child_nodes)
            current_nodes = next_nodes
            next_nodes = []

        assert all(n.depth == n.max_depth for n in next_nodes)

        game = Game(top_node, all_nodes)
        return game

    def save_game(self, file_path):
        game_config = self.top_node.game_config.to_json_dict()
        game_config["nr_nodes"] = len(self.node_mapping)
        game_config["nr_leaves"] = self.nr_leaves
        json_data = {"config": game_config, "game": []}
        for node_id, node in self.node_mapping.items():
            json_data["game"].append(node.to_json())
        with open(file_path, "w") as outfile:
            json.dump(json_data, outfile, indent=2)

    @staticmethod
    def from_json(game_data):
        game_config = GameConfiguration.from_json_dict(game_data['config'])
        game = Game.new_game_creation(game_config)
        nodes = {gd['node_id']: gd for gd in game_data['game']}
        assert set(game.node_mapping.keys()) == set(nodes.keys())

        # not replacing the top_node reference here
        for node_id in game.node_mapping.keys():
            game.node_mapping[node_id] = GameNode.from_json(nodes[node_id], game_config)
        game.top_node = game.node_mapping[game.top_node.node_id]
        return game
