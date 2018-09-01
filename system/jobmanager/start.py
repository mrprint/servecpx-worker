# -*- coding: utf8

__author__ = 'nolka'

import logging
from timeit import default_timer as timer

from manager import JobManager
from workers.urlparser import UrlParser, NamedUrlParser


def main():
    def result_handler(manager, results):
        """
        Handle worker results
        :param manager: JobManager
        :param results: Queue
        """
        while True:
            task = results.get()
            ":type task: SimpleTask"
            if task is None:
                print ("RH: Received poison...")
                break
            else:
                print("Received task id: %d with result length: %s" % (task.id, task.result))

    start = timer()

    logger = logging.getLogger("jobmanager.JobManager")
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
    logger.addHandler(console)

    m = JobManager(result_handler, logger)

    m.add_workers(NamedUrlParser('ololo'), NamedUrlParser('trololo'), UrlParser(), UrlParser())
    m.do_work()

    listen_files = [
        "http://stackoverflow.com",
        "http://caldina-club.com",
        "http://www.land-cruiser.ru",
        "http://habrahabr.ru",
        "http://pikabu.ru",
        "http://stackoverflow.com",
        "http://caldina-club.com",
        "http://www.land-cruiser.ru",
        "http://habrahabr.ru",
        "http://pikabu.ru",
    ]

    for url in listen_files:
        logging.info("added job %s" % url)
        m.add_job(url)

    logging.warn("Finalizing :D")

    m.exit()

    logging.warn("Done!")
    print (timer() - start)


if __name__ == "__main__":
    main()