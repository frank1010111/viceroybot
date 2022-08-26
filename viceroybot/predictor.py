"""Predict text using Markov chains."""

from __future__ import annotations

import json
from random import choice


def build_queue(
    queue_file: str, markov_chain: dict, prompts: list[str]
) -> list[dict[str, str | bool]]:
    """Append new tweets to the queue.

    Parameters:
        queue_file (json) - existing queue file to append to
        markov_chain - Markov chain to work off of
        prompts - the strings to feed into the Markov chain to start things off

    Returns:
        queue (a list)
    """
    with open(queue_file) as f:
        queue = json.load(f)
    if queue:
        idx = max(x["id"] for x in queue)
    else:
        idx = 0
    for p in prompts:
        idx += 1
        tries = 0
        while tries < 50:
            tries += 1
            text = write_from_markov_chain(markov_chain, n_words=60, prompt=p)
            text = twitterify(text)
            if len(text) > 130:
                break
        queue.append({"id": idx, "text": text, "sent": False})
    return queue


def twitterify(text, limit=280):
    """Make text fit into twitter character limit."""
    if len(text) > limit:
        j = limit - 1
        while text[j] not in (".", "?", "!", ";"):
            j -= 1
        text = text[: j + 1]
        if text[-1] == ";":
            text = text[:-1] + "."
    return text


def write_from_markov_chain(
    markov_chain: dict[tuple[str], str], n_words: int = 100, prompt: str | None = None
):
    """Generate text given a markov chain.

    Args:
        markov_chain (dict): predicting tool
        n_words (int): number of words to generate
        prompt (str): text to start with
    Returns:
        generated text
    """
    last_prefix_lookup = {}
    for key in markov_chain:
        prefix = key[-1]
        if prefix not in last_prefix_lookup:
            last_prefix_lookup[prefix] = []
        last_prefix_lookup[prefix].append(markov_chain[key])
    prefix_list = list(markov_chain)
    if prompt is None:
        prefix = choice(prefix_list)
    else:
        prefix = tuple(prompt.split())
    out = " ".join(prefix)
    for _i in range(n_words):
        if prefix not in markov_chain:
            if prefix in last_prefix_lookup:
                suffix = choice(last_prefix_lookup[prefix[-1]])
            else:
                suffix = choice(list(markov_chain[choice(prefix_list)]))
        else:
            suffix = choice(list(markov_chain[prefix]))
        out += " " + suffix
        prefix = tuple(list(prefix[1:]) + [suffix])
    return out


def train_markov_chain(files: list[str]):
    """Train Markov chain from input files."""
    markov_chain = {}
    for fname in files:
        with open(fname) as f:
            for line in f.readlines():
                markov_chain = update_markov_chain(line, markov_chain, n_pref=3)
    return markov_chain


def update_markov_chain(line: str, chain: dict[tuple, str], n_pref: int = 2):
    """Update existing Markov chain with new line.

    Args:
        line (str) new line of text
        chain (dict) existing Markov chain
        n_pref (int) number of prefix terms
    Return: return_description
    """
    words = line.split()  # .replace('—',' ')
    if len(words) < n_pref + 1:
        return chain
    for i in range(n_pref, len(words)):
        prefix = tuple(words[i - n_pref : i])
        suf = words[i]
        if prefix not in chain:
            chain[prefix] = set()
        chain[prefix].add(suf)
    return chain


def count_elements(seq) -> dict:
    """Tally elements from `seq`."""
    histogram = {}
    for i in seq:
        histogram[i] = histogram.get(i, 0) + 1
    return histogram
