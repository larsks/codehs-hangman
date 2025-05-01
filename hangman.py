import sys
import random
from collections import defaultdict
from functools import cache

import rich.console
import rich.panel
import rich.prompt

from asciiart import HANGMANPICS, TOMBSTONE, AWARD, BROWN, RESET, RED, GREEN

DEFAULT_WORDFILE = "words.txt"
MAX_INCORRECT_GUESSES = len(HANGMANPICS) - 1
MAX_HINTS = 2
BLANK = "-"

class Display:
    def __init__(self):
        self.console = rich.console.Console()

    def clear(self):
        self.console.clear()

    def panel(self, text):
        self.console.print(rich.panel.Panel(text))

    def error(self, text):
        self.console.print(f"[red]{text}")

    def warn(self, text):
        self.console.print(f"[yellow]{text}")

    def success(self, text):
        self.console.print(f"[green]{text}")

    def prompt(self, prompt):
        return rich.prompt.Prompt().ask(prompt)

class Hangman:
    def __init__(self, wordfile=None):
        self.display = Display()
        self.wordfile = wordfile if wordfile else DEFAULT_WORDFILE
        self.words = defaultdict(list)
        self.read_words()

    def read_words(self):
        try:
            with open(self.wordfile) as fd:
                for word in (line.strip() for line in fd):
                    if not word or word.startswith("#"):
                        continue
                    self.words[len(word)].append(word)
        except FileNotFoundError:
            sys.exit(f"Unable to read words from file {self.wordfile}.")

    def select_random_word(self, length):
        return random.choice(self.words[length])

    def display_status(self):
        print("\nWord: ", " ".join(self.current_progress))
        print(
            f"Guessed: {', '.join(sorted(self.guessed_letters)) if self.guessed_letters else 'None'}"
        )
        print(f"Remaining incorrect guesses: {self.remaining_guesses}")

    def display_gallows(self):
        self.display.panel(f"[dark_goldenrod]{HANGMANPICS[len(HANGMANPICS) - self.remaining_guesses - 1]}")

    def get_valid_guess(self):
        while True:
            guess = (
                self.display.prompt("[yellow]Guess a letter (or type 'hint' for a hint)").lower().strip()
            )
            if guess == "hint":
                return "hint"
            elif len(guess) != 1 or not guess.isalpha():
                self.display.error("Invalid input. Enter a single letter.")
            elif guess in self.guessed_letters:
                self.display.error("You already guessed that letter.")
            else:
                return guess

    def guess_letter(self, letter):
        self.guessed_letters.add(letter)

        if letter in self.word:
            self.display.success(f"Good guess! '{letter}' is in the word.")
            for i, char in enumerate(self.word):
                if char == letter:
                    self.current_progress[i] = letter
        else:
            self.remaining_guesses -= 1
            self.display.error(f"Wrong guess! '{letter}' is not in the word.")

    def hint(self):
        if not self.available_hints:
            self.display.error("You have already used all your available hints!")
            return
        letter = None
        self.available_hints -= 1
        for i, blank in enumerate(self.current_progress):
            if letter is None:
                if blank == BLANK:
                    letter = self.word[i]
                    self.guessed_letters.add(letter)

            if letter is not None:
                if self.word[i] == letter:
                    self.current_progress[i] = letter

    def is_won(self):
        return BLANK not in self.current_progress

    def is_lost(self):
        return self.remaining_guesses <= 0

    def play(self):
        self.display.clear()
        self.display.panel("Welcome to [red]Hangman!")

        length = self.choose_word_length()
        self.guessed_letters = set()
        self.current_progress = [BLANK] * length
        self.word = self.select_random_word(length)
        self.remaining_guesses = MAX_INCORRECT_GUESSES
        self.available_hints = MAX_HINTS

        self.display_gallows()
        while not self.is_won() and not self.is_lost():
            self.display_status()
            letter = self.get_valid_guess()
            if letter == "hint":
                self.hint()
            else:
                self.guess_letter(letter)
            self.display_gallows()

        if self.is_won():
            self.display.panel(f"[green]🎉 You won! The word was: {self.word}\n\n{AWARD}")
        else:
            self.display.panel(f"[red]💀 You lost! The word was: {self.word}\n\n{TOMBSTONE}")

    @cache
    def word_lengths(self):
        return sorted(x for x in self.words.keys() if x > 1)


    def choose_word_length(self):
        while True:
            try:
                length = int(
                    input(
                        f"Choose word length ({', '.join(str(x) for x in self.word_lengths())}): "
                    )
                )
                if length in self.word_lengths():
                    return length
                print("Invalid length.")
            except ValueError:
                print("Please enter a number.")


def main():
    game = Hangman()
    game.play()


if __name__ == "__main__":
    main()
