"""
A simple CLI tool to work with flashcards defined in a CSV file, made with Python 3

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
import os

GREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
RED = "\x1b[1;31m"
REVERSE = "\x1b[7m"
RESET = "\x1b[0m"

def clear_terminal():
    """Clears the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_ascii_box_with_text(width: int, height: int, text: str, flipped: bool):
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
    
    for line in lines:
        if len(line) > width:
            width = len(line)+2

    # Adjust height to fit wrapped text
    height = max(height, len(lines) + 2)

    if flipped:
        print(REVERSE, end='')
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
    if flipped:
        print(RESET, end='')

def print_titlebar(filename: str):
    cols = os.get_terminal_size().columns
    title = f"flashcards.py - {filename}"
    padding = (cols - len(title)) // 2
    print(REVERSE + " " * padding + title + " " * (cols - len(title) - padding) + RESET)
    print()

def print_stats(correct: int, review: int, total: int):
    """Prints the current statistics"""
    print(f"Stats: ✅ {GREEN}{correct}{RESET}, 📖 {YELLOW}{review}{RESET}, Total Cards: {total}")

def find_most_reviewed_card(flashcard_review_counts: dict[str, int]) -> str:
    """Returns the most reviewed card in the set"""
    most = 0
    most_card = flashcard_review_counts.keys
    for card, count in flashcard_review_counts.items():
        if count > most:
            most = count
            most_card = card
    
    return most_card if most != 0 else None

def print_end_stats(verbose: bool, correct: int, review_count: int, flashcard_review_counts: dict[str,int]):
    """Prints the statistics at the end of the session"""
    print(f"Study Session Results:\n\t✅ Correct: {correct}\n\t📖 Needed to Review: {review_count}")
    if verbose:
        print("Individual Card Statistics")
        for card, review_count in flashcard_review_counts.items():
            colour = ""
            if review_count == 0:
                colour = GREEN
            elif review_count <= 3:
                colour = YELLOW
            else:
                colour = RED
            print(f"\t({card}) Times to Review: {colour}{review_count}{RESET}")
    else:
        most_card = find_most_reviewed_card(flashcard_review_counts)
        if most_card:
            print(f"Most Reviewed Card: '{most_card}'")

def parse_flashcards(output: list[tuple[str, str]], stats_output: dict[str, int], f):
    """Parses the CSV file containing the flash cards"""
    csvreader = csv.reader(f)
    for row in csvreader:
        front = row[0]
        back = row[1]
        if len(row) != 2:
            back = ",".join(row[1:])
        output.append((front, back))
        stats_output[row[0]] = 0

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

    initial_flashcards: list[tuple[str, str]] = []
    flashcard_review_counts = {}
    correct = 0
    cards_to_review = set()

    try:
        with open(args.filename, "r", newline="") as f:
            parse_flashcards(initial_flashcards, flashcard_review_counts, f)

    except FileNotFoundError:
        print(f"ERROR: Could not read {args.filename}")
        return

    flashcards = initial_flashcards.copy()
    if args.shuffle:
        random.shuffle(flashcards)
    total_cards = len(flashcards)

    running = True
    flipped = False
    while running:
        clear_terminal()
        print_titlebar(args.filename)
        if len(flashcards) == 0:
            running = False
            break
        
        flashcard = flashcards[0]
        front = flashcard[0]
        back = flashcard[1]
        output_text = front
        if flipped:
            output_text = back

        draw_ascii_box_with_text(32, 9, output_text, flipped)
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
                    flashcards.pop(0)
                    flipped = False
                    valid_action = True
                    correct += 1
                    break
                case "r":
                    flipped = False
                    valid_action = True
                    cards_to_review.add(front)
                    flashcard_review_counts[front] += 1
                    # move the flashcard to the back of the queue
                    card = flashcards.pop(0)
                    flashcards.append(card)
                    break
                case "f":
                    flipped = not flipped
                    valid_action = True
                case _:
                    print("Unknown action")
                    valid_action = False
        
    print_end_stats(args.verbose, correct, len(cards_to_review), flashcard_review_counts)


if __name__ == "__main__":
    main()
