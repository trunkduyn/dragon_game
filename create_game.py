import argparse
import json

from game_src.game import Game
from game_src.game_configuration import GameConfiguration


def ask_continue(game: Game):
    response = input("do you want to continue? (y) or quit (q)?")
    if response == 'y':
        return
    if response == 'q':
        game.save_game(args.file_path)
        exit()


fake_result = ["draak vlieg", "hide", "attack", "make friend"]
positive_chat_gpt_fraction = 2 / 3
max_gpt_words = 50


def continue_game_creation(game: Game):
    count = 0
    for node, story, node_nr in game.traverse_depth_first_and_yield_empty_texts():
        content = node.node_content
        if node.node_id == "d00n00":
            x=2

        # fill description if necessary
        if not content.situation_description:
            display_story(story, node.node_id)
            result = input("Provide a situation description:\n")
            # result = f"{fake_result[0]} N{count}"
            content.situation_description = result
            story = story + [result]
        else:
            story = story + [content.situation_description]

        # fill option texts
        if not all(content.option_texts.values()):
            display_story(story, node.node_id)
            if args.chat_gpt_format:
                print(f"Can you list {len(content.option_texts)} very different but specific actions that a character could take next and phrase them as action options to a user?")
            option_texts = {}
            for i, option_id in enumerate(content.option_texts.keys()):
                result = input(f"Provide action {i} that could be taken by the player:\n")
                # result = f"{fake_result[i + 1]} N{count}"
                option_texts[option_id] = result
            content.option_texts = option_texts

        # handle outcomes to options
        if content.is_leaf:
            final_outcome_texts = {}
            for i, option_id in enumerate(content.option_texts.keys()):
                outcome_story = story + [content.option_texts[option_id]]
                display_story(outcome_story, node.node_id)
                if args.chat_gpt_format:
                    nr_answer_outcomes = node.game_config.nr_answer_outcomes
                    nr_positive = int(positive_chat_gpt_fraction * nr_answer_outcomes)
                    print(f"Can you list {nr_answer_outcomes} different things that could happen next of which {nr_positive} result in a gift and in the other ones the gift is lost?")

                for j, outcome_id in enumerate(content.option_to_outcome_mapping[option_id]):
                    result = input(f"[Node{node_nr}/{len(game.node_mapping)}] Provide outcome {j} that could occur\n")
                    # result = f"fake_result_{i}_{j}"
                    final_outcome_texts[outcome_id] = result

            content.final_outcome_texts = final_outcome_texts

        elif args.chat_gpt_format:
            # Gather texts now in gpt format because you want to list them at once
            for i, option_id in enumerate(content.option_texts.keys()):
                outcome_story = story + [content.option_texts[option_id]]
                display_story(outcome_story, node.node_id)
                print(f"What could happen next? Can you list {node.game_config.nr_answer_outcomes} small continuations of the story in second person in max {max_gpt_words} words?")
                # put the text in descriptions of child nodes
                for j, outcome_id in enumerate(content.option_to_outcome_mapping[option_id]):
                    result = input(f"[Node{node_nr}/{len(game.node_mapping)}] Provide outcome {j} that could occur\n")
                    next_node = game.node_mapping[content.next_node_ids[outcome_id]]
                    next_node.node_content.situation_description = result

        # after every node
        game.save_game('temp_save.json')
        count += 1
    game.save_game("temp_final.json")


def display_story(story, node_id):
    message = f"\n[{node_id}] Preceding story:\n"
    print(message + '-' * len(message))
    print("\n".join(story))


def load_game(file_path):
    with open(file_path) as inpath:
        game_data = json.load(inpath)
    game = Game.from_json(game_data)
    game.save_game('test_file2.json')
    return game


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Start creating the game',
    )

    parser.add_argument('file_path', type=str, help='path to game file (new or continue')
    parser.add_argument('--continue_game', '-g', action='store_true', help='continue creating a game')
    parser.add_argument('--depth', '-d', type=int, default=3, help='depth of game graph')
    parser.add_argument('--nr_answers', '-a', type=int, default=3, help='number of possible answers per choice in node')
    parser.add_argument('--nr_outcomes', '-o', type=int, default=2, help='nr outcomes per choice answer')
    parser.add_argument('--dice', type=int, default=1, help='number of dice used for the game')
    parser.add_argument('--chat_gpt_format', '-c', action='store_true', help='continue creating a game')

    args = parser.parse_args()

    if args.continue_game:
        game = load_game(args.file_path)
        continue_game_creation(game)
        game.save_game(args.file_path)
    else:
        assert (args.dice * 6) % args.nr_outcomes == 0

        game_config = GameConfiguration(args.dice, args.nr_answers, args.nr_outcomes, args.depth)
        game = Game.new_game_creation(game_config)
        game.save_game(args.file_path)
