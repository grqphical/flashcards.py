"""
A simple CLI tool to work with flashcards, made with Python 3

Author: Nathan Jacobson <https://nathanjacobson.ca>
"""
import argparse
import csv

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