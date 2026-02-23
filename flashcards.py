"""
A simple CLI tool to work with flashcards, made with Python 3

Author: Nathan Jacobson <https://nathanjacobson.ca>

Repository: <https://github.com/grqphical/flashcards.py>

Usage:
    flashcards.py [-h] [-s] [-v] filename
    positional arguments:
        filename

    options:
    -h, --help     show this help message and exit
    -s, --shuffle  Whether or not flashcards are shuffled
    -v, --verbose  Shows more detailed statistics at the end

License:

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
"""

import argparse
import csv
import random

GREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
RED = "\x1b[1;31m"
RESET = "\x1b[0;39m"

def clear_terminal():
    """Clears the terminal and moves the cursor back to the home position"""
    print("\x1b[2J")
    print("\x1b[H")


def draw_ascii_box_with_text(width: int, height: int, text: str):
    """Draws a box with text around it. Used to draw nicer looking flashcards"""
    # Wrap text to fit within box width
    max_text_width = width - 4
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_text_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    # Adjust height to fit wrapped text
    height = max(height, len(lines) + 2)

    # Top border
    print("+" + "-" * (width - 2) + "+")

    text_start = (height - len(lines)) // 2

    for i in range(1, height - 1):
        if text_start <= i < text_start + len(lines):
            line_idx = i - text_start
            text_line = lines[line_idx]
            padding_total = width - 2 - len(text_line)
            left_pad = padding_total // 2
            right_pad = padding_total - left_pad
            print("|" + " " * left_pad + text_line + " " * right_pad + "|")
        else:
            print("|" + " " * (width - 2) + "|")

    # Bottom border
    print("+" + "-" * (width - 2) + "+")

def print_stats(correct: int, review: int, total: int):
    """Prints the current statistics"""
    print(f"Stats: ✅ {GREEN}{correct}{RESET}, 📖 {YELLOW}{review}{RESET}, Total Cards: {total}")

def find_most_reviewed_card(flashcard_stats: dict[str, int]) -> str:
    """Returns the most reviewed card in the set"""
    most = 0
    most_card = flashcard_stats.keys
    for card, count in flashcard_stats.items():
        if count > most:
            most = count
            most_card = card
    
    return most_card if most != 0 else "None"

def print_end_stats(verbose: bool, correct: int, review_count: int, flashcard_stats: dict[str,int]):
    """Prints the statistics at the end of the session"""
    print(f"Study Session Results:\n\t✅ Correct: {correct}\n\t📖 Needed to Review: {review_count}")
    if verbose:
        print("Individual Card Statistics")
        for card, review_count in flashcard_stats.items():
            colour = ""
            if review_count == 0:
                colour = GREEN
            elif review_count <= 3:
                colour = YELLOW
            else:
                colour = RED
            print(f"\t({card}) Times to Review: {colour}{review_count}{RESET}")
    else:
        print(f"Most Reviewed Card: '{find_most_reviewed_card(flashcard_stats)}'")


def main():
    parser = argparse.ArgumentParser(
        prog="flashcards.py",
        description="A simple flashcard tool that reads flashcards from a CSV file",
        epilog="Made by Nathan Jacobson <https://github.com/grqphical/flashcards.py>"
    )

    parser.add_argument("filename")
    parser.add_argument("-s", "--shuffle", help="Whether or not flashcards are shuffled", action="store_true")
    parser.add_argument("-v", "--verbose", help="Shows more detailed statistics at the end", action="store_true")

    args = parser.parse_args()

    initial_flashcards = {}
    flashcard_stats = {}
    correct = 0
    cards_to_review = set()

    try:
        with open(args.filename, "r", newline="") as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                back = row[1]
                if len(row) != 2:
                    back = ",".join(row[1:])
                initial_flashcards[row[0]] = back
                flashcard_stats[row[0]] = 0

    except FileNotFoundError:
        print(f"ERROR: Could not read {args.filename}")

    flashcards = initial_flashcards.copy()
    total_cards = len(flashcards)
    

    idx = 0
    running = True
    flipped = False
    while running:
        clear_terminal()
        if len(flashcards) == 0:
            running = False
            break

        if args.shuffle and idx == 0:
            idx = random.randint(0, len(flashcards) - 1)

        front = list(flashcards.keys())[idx]
        output_text = front
        if flipped:
            output_text = flashcards[front]

        draw_ascii_box_with_text(32, 9, output_text)
        print_stats(correct, len(cards_to_review), total_cards)
        print("\nActions: 'f' to flip, 'q' to quit, 'c' to mark card as correct, 'r' to mark card for further review")

        valid_action = False
        while not valid_action:
            action = input("> ")

            match action:
                case "q":
                    valid_action = True
                    running = False
                case "c":
                    del flashcards[front]
                    flipped = False
                    valid_action = True
                    correct += 1
                    if len(flashcards) != 0:
                        idx = random.randint(0, len(flashcards) - 1)
                    break
                case "r":
                    flipped = False
                    valid_action = True
                    cards_to_review.add(front)
                    flashcard_stats[front] += 1
                    if len(flashcards) != 0:
                        idx = random.randint(0, len(flashcards) - 1)
                    break
                case "f":
                    flipped = not flipped
                    valid_action = True
                case _:
                    print("Unknown action")
                    valid_action = False
        
    print_end_stats(args.verbose, correct, len(cards_to_review), flashcard_stats)


if __name__ == "__main__":
    main()
