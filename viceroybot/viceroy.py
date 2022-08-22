"""Viceroy can be used to generate text and even tweet it out.

To use trends and tweets, you need to sign up for Twitter's API to get bearer
and access tokens, then load them into the system environment or a .env file
in the directory where you are running this.

Subcommands:
train: train the text generation on input files
generate: generate text following your choice of first words
trends: generate text about twitter trending topics
tweet: tweet generated text

"""
from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from random import choice

import click

from viceroybot.predictor import (
    build_queue,
    train_markov_chain,
    write_from_markov_chain,
)
from viceroybot.tweet import get_trending, tweet_from_queue

os.makedirs(".viceroy", exist_ok=True)
MODEL_FILE = Path(".viceroy/trained_model.pkl")
QUEUE_FILE = Path(".viceroy/tweet_queue.json")


@click.group()
def viceroy():
    """Command line tools for working with text generation and twitter."""
    pass


@viceroy.command()
@click.argument("inputs", nargs=-1, type=click.Path(exists=True))
# @click.option("--output", type=click.Path())
def train(inputs):
    """Train Markov chain on all files."""
    markov_chain = train_markov_chain(inputs)
    with open(MODEL_FILE, "wb") as file:
        pickle.dump(markov_chain, file)


@viceroy.command()
@click.argument("prompt", nargs=-1)
@click.option("-n", "--n-words", type=int)
def generate(prompt, n_words):
    """Generate text given the prompt."""
    if not MODEL_FILE.exists():
        click.ClickException("Must train model with `viceroy train` to generate")
    with open(MODEL_FILE) as f:
        markov_chain = pickle.load(f)
    output = write_from_markov_chain(markov_chain, n_words, prompt)
    click.echo(output)


@viceroy.command()
@click.option("-l", "--location", default="USA", show_default=True)
def trends(location):
    """Get the trending topics."""
    trending = get_trending(location)
    click.echo("Trends:")

    for trend in trending:
        click.echo(trend)


@viceroy.command()
@click.option("-r", "--raw", is_flag=True)
@click.argument("prompt", type=str, nargs=-1)
def queue(raw: bool, prompt=list[str]):
    """Add to tweet queue.

    If no prompt is given, get Twitter trending topics and use one of them.
    """
    if prompt:
        prompts = [" ".join(prompt)]
    else:
        prompts = [choice(get_trending("USA"))]
        click.echo("prompts are\n  " + "\n  ".join(prompts))
    if raw:
        with open(QUEUE_FILE) as file:
            queue = json.load(file)
        id = max(tweet["id"] for tweet in queue) + 1
        queue.append({"id": id, "text": prompt, "sent": False})
    else:
        with open(MODEL_FILE, "rb") as file:
            markov_chain = pickle.load(file)
        queue = build_queue(QUEUE_FILE, markov_chain, prompts)
    click.echo("The new tweet will be:\n  " + queue[-1]["text"])
    with open(QUEUE_FILE, "w") as file:
        json.dump(queue, file, indent=2)


@viceroy.command()
@click.option("-q/-n", "--from_queue/--not_from_queue", default=True)
@click.argument("tweet-text", type=str, default="")
def tweet(from_queue: bool = True, tweet_text: str = ""):
    """Tweet from either tweet queue or your own text."""
    if tweet_text and from_queue:
        click.ClickException(
            "can't use both --from-queue and tweet-text at the same time"
        )
    elif tweet_text and not from_queue:
        with open(QUEUE_FILE) as file:
            queue = json.load(file)
        sent_tweets = [tweet for tweet in queue if tweet["sent"]]
        unsent_tweets = [tweet for tweet in queue if not tweet["sent"]]
        id = max(tweet["id"] for tweet in queue) + 1
        queue_out = (
            sent_tweets
            + [{"id": id, "text": tweet_text, "sent": False}]
            + unsent_tweets
        )
        with open(QUEUE_FILE, "w") as file:
            json.dump(queue_out)
    tweet_from_queue(QUEUE_FILE)
