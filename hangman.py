import sys
import random
from collections import defaultdict
from functools import cache

from asciiart import HANGMANPICS, TOMBSTONE, AWARD, BROWN, RESET, RED, GREEN

DEFAULT_WORDFILE = "words.txt"
MAX_INCORRECT_GUESSES = len(HANGMANPICS) - 1
MAX_HINTS = 2
BLANK = "-"

class Hangman:
    def __init__(self, wordfile=None):
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
        print(BROWN)
        print(HANGMANPICS[len(HANGMANPICS) - self.remaining_guesses - 1])
        print(RESET)

    def get_valid_guess(self):
        while True:
            guess = (
                input("Guess a letter (or type 'hint' for a hint): ").lower().strip()
            )
            if guess == "hint":
                return "hint"
            elif len(guess) != 1 or not guess.isalpha():
                print(f"{RED}Invalid input. Enter a single letter.{RESET}")
            elif guess in self.guessed_letters:
                print(f"{RED}You already guessed that letter.{RESET}")
            else:
                return guess

    def guess_letter(self, letter):
        self.guessed_letters.add(letter)

        if letter in self.word:
            print(f"{GREEN}Good guess! '{letter}' is in the word.{RESET}")
            for i, char in enumerate(self.word):
                if char == letter:
                    self.current_progress[i] = letter
        else:
            self.remaining_guesses -= 1
            print(f"{RED}Wrong guess! '{letter}' is not in the word.{RESET}")

    def hint(self):
        if not self.available_hints:
            print(f"{RED}You have already used all your available hints!{RESET}")
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

    def play(self, length):
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
            print(f"\n🎉 You won! The word was: {self.word}")
            print(AWARD)
        else:
            print(f"\n💀 You lost! The word was: {self.word}")
            print(TOMBSTONE)

    @cache
    def word_lengths(self):
        return sorted(x for x in self.words.keys() if x > 1)


def choose_word_length(game):
    while True:
        try:
            length = int(
                input(
                    f"Choose word length ({', '.join(str(x) for x in game.word_lengths())}): "
                )
            )
            if length in game.word_lengths():
                return length
            print("Invalid length.")
        except ValueError:
            print("Please enter a number.")


def main():
    game = Hangman()
    length = choose_word_length(game)
    game.play(length)


if __name__ == "__main__":
    main()
