import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-t",
    "--token",
    help="provide a token to add the emojis as, can be client token or bot token",
)
parser.add_argument(
    "-g",
    "--guild-id",
    help="provide a guild id to add the emojis to (required) Note: the bot must be in that guild",
    type=int,
)
parser.add_argument(
    "-d",
    "--debug",
    help="if used then the logging level is set to DEBUG",
    action="store_true",
)
parser.add_argument(
    "-o",
    "--output",
    help="provide a filename to add the emojis to (optional, defaults to emojis.json)",
)
