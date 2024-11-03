import logging
import sys

from argparse import ArgumentParser

from backerupper import BackerUpper


def main(*args, **kwargs):
    backerupper = BackerUpper()
    backerupper(*args, **kwargs)


if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html
    parser = ArgumentParser(
        description="A Python script to create and manage backup archives",
    )
    parser.add_argument(
        "source",
        help="Source file or directory path to create a backup",
    )
    parser.add_argument(
        "--to",
        dest="destination",
        help="Destination directory path for backups \
        (default: parent directory of source)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=10,
        dest="retention_count",
        help="Retention count of N previous backups to keep. \
        Use -1 to keep all previous backups at the destination \
        (default: 10)",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Use a sequential suffix for backup names (.1, .2, ...) \
        A UTC date+time stamp (YYYY-mm-ddTHH-MM-SS-fZ) is used by default \
        (default: False)",
    )
    parser.add_argument(
        "--uncompressed",
        action="store_true",
        help="Disable GZIP compression (default: False)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Run with verbose messages enabled",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run with noisy debug messages enabled",
    )
    # Parse all arguments
    argv, remaining_argv = parser.parse_known_args()

    # Configure logging
    # https://docs.python.org/3/howto/logging.html
    if argv.debug:
        log_level = logging.DEBUG
    elif argv.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    log_format = "[%(asctime)s] %(levelname)s - %(message)s"
    log_datefmt = "%Y-%m-%d %H:%M:%S %Z"
    logging.basicConfig(
        format=log_format,
        datefmt=log_datefmt,
        level=log_level,
    )
    logging.debug(f"{__name__} - sys.argv: {sys.argv}")
    logging.debug(f"{__name__} - argv: {argv}")

    # Debug argv attributes
    if argv.debug:
        for key, value in vars(argv).items():
            logging.debug(f"{__name__} - argv.{key} {type(value)}: {value!r}")

    # Run the program
    try:
        # Pass all parsed arguments to the main function as key word arguments
        main(**vars(argv))
    except Exception as err:
        logging.error(f"{sys.exc_info()[0]}; {err}")
        # Cause the program to exit on error when running in debug mode
        if hasattr(argv, "debug") and argv.debug:
            raise
