import logging

logging.basicConfig(
    filename="log.txt",
    filemode="a"
)


def log(msg):
    logging.error(msg)
