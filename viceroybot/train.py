from viceroybot.predictor import train_markov_chain

if __name__ == "__main__":
    import pickle
    import argparse

    parser = argparse.ArgumentParser(
        description="Build Markov chain and output pickled dictionary specification"
    )
    parser.add_argument("infile", metavar="INFILE", nargs="+")
    parser.add_argument("--out", "-o", metavar="OUTFILE", default=None)
    args = parser.parse_args()
    markov_chain = train_markov_chain(args.infile)
    if args.out is None:
        print(pickle.dumps(markov_chain))
    else:
        with open(args.out, "wb") as f:
            pickle.dump(markov_chain, f)
