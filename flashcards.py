"""
A simple CLI tool to work with flashcards, made with Python 3

Author: Nathan Jacobson <https://nathanjacobson.ca>
"""
import argparse
import csv
import random

def clear_terminal():
    print(chr(27) + "[2J")

def draw_ascii_box_with_text(width, height, text):
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
    print('+' + '-' * (width - 2) + '+')
    
    vertical_center = height // 2
    text_start = (height - len(lines)) // 2
    
    for i in range(1, height - 1):
        if text_start <= i < text_start + len(lines):
            line_idx = i - text_start
            text_line = lines[line_idx]
            padding_total = width - 2 - len(text_line)
            left_pad = padding_total // 2
            right_pad = padding_total - left_pad
            print('|' + ' ' * left_pad + text_line + ' ' * right_pad + '|')
        else:
            print('|' + ' ' * (width - 2) + '|')
    
    # Bottom border
    print('+' + '-' * (width - 2) + '+')

parser = argparse.ArgumentParser(
    prog="flashcards.py",
    description="A simple flashcard tool that reads flashcards from a CSV file"
)

parser.add_argument('filename')
parser.add_argument('-s', '--shuffle', action="store_true")

args = parser.parse_args()

flashcards = {}

try:
    with open(args.filename, "r", newline='') as f:
        csvreader = csv.reader(f)
        for i, row in enumerate(csvreader):
            if i == 0:
                continue # skip header row
            back = row[1]
            if len(row) != 2:
                back = ",".join(row[1:])
            flashcards[row[0]] = back
            
except FileNotFoundError:
    print(f"ERROR: Could not read {args.filename}")

idx = 0
flipped = False
while True:
    
    clear_terminal()
    if args.shuffle:
        idx = random.randint(0, len(flashcards)-1)
    
    front = list(flashcards.keys())[idx]
    output_text = front
    if flipped:
        output_text = flashcards[front]

    draw_ascii_box_with_text(32, 9, output_text)
    print("\nActions: 'f' to flip, 'q' to quit, 'n' to move onto next card")
    action = input("> ")

    match action:
        case "q":
            break
        case "n":
            del flashcards[front]
            flipped = False
            continue
        case "f":
           flipped = not flipped