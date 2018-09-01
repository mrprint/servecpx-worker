__author__ = 'nolka'

from runner import Runner


def main():
    r = Runner('test_modules')
    r.run('test_run.Main')

if __name__ == "__main__":
    main()