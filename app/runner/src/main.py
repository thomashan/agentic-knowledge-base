import structlog

log = structlog.get_logger()


def main():
    log.info("hello world main!")


if __name__ == "__main__":
    main()
