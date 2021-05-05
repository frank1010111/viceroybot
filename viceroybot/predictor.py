from random import choice, choices
import pickle
import json
from viceroybot.tweet import get_trending


def build_queue(queue_file: str, markov_chain: dict, prompts: list) -> list:
    """Appends new tweets to the queue

    Parameters:
        queue_file (json) - existing queue file to append to
        markov_chain - Markov chain to work off of
        prompts - the strings to feed into the Markov chain to start things off

    Returns:
        queue (a list)
    """
    with open(queue_file, "r") as f:
        queue = json.load(f)
    idx = max(x["id"] for x in queue)
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
    "Make text fit into twitter character limit"
    if len(text) > limit:
        j = limit - 1
        while text[j] not in (".", "?", "!", ";"):
            j -= 1
        text = text[: j + 1]
        if text[-1] == ";":
            text = text[:-1] + "."
    return text


def write_from_markov_chain(markov_chain, n_words=100, prompt=None):
    prefix_list = list(markov_chain)
    last_prefix_lookup = {p[-1]: p for p in markov_chain}
    if prompt is None:
        prefix = choice(prefix_list)
    else:
        prefix = tuple(prompt.split())
    out = " ".join(prefix)
    for i in range(n_words):
        if prefix not in markov_chain:
            try:
                prefix = last_prefix_lookup[prefix[-1]]  # note, this is deterministic
            except KeyError:  # for the last word in a paragraph
                prefix = choice(prefix_list)
        suffix = choice(list(markov_chain[prefix]))
        out += " " + suffix
        prefix = tuple(list(prefix[1:]) + [suffix])
    return out


def train_markov_chain(files):
    markov_chain = {}
    for fname in files:
        with open(fname, "r") as f:
            for line in f.readlines():
                markov_chain = update_markov_chain(line, markov_chain, n_pref=3)
    return markov_chain


def update_markov_chain(line, chain={}, n_pref=2):
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
    hist = {}
    for i in seq:
        hist[i] = hist.get(i, 0) + 1
    return hist


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add to queue from trending tweets")
    parser.add_argument(
        "spec_file", metavar="SPEC_FILE", nargs="+", help="specification file (pickle)"
    )
    parser.add_argument(
        "--train", "-t", action="store_true", help="train Markov chain from text"
    )
    parser.add_argument("--queue", "-q", help="queue file", default="tweet_queue.json")
    parser.add_argument(
        "--location", "-l", help="twitter location for trends", default="USA"
    )
    parser.add_argument(
        "--max_trends", type=int, default=8, help="upper limit on trends to use"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="increase output verbosity"
    )
    args = parser.parse_args()
    if args.train:
        markov_chain = train_markov_chain(args.spec_file)
    else:
        with open(args.spec_file[0], "rb") as f:
            markov_chain = pickle.load(f)
    trends = get_trending(args.location)
    if len(trends) > args.max_trends:
        trends = choices(trends, k=args.max_trends)
    new_queue = build_queue(args.queue, markov_chain, trends)
    if args.verbose >= 1:
        print(f"{len(trends)} trends captured")
    if args.verbose >= 2:
        print("trends include:")
        for t in trends:
            print("  ", t)
    with open(args.queue, "w") as f:
        json.dump(new_queue, f, indent=2)
