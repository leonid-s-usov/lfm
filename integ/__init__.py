'''Lambda integration tests.

To run, you will need the following:

  - AWS credentials and region defined in ~/.aws/credentials
  - A default execution role specified in ~/.aws/lambda.yml
  - A local virtual environment `env`, such that while in the
    root of this repository, running `env/bin/python lfm` is
    equivalent to invoking lfm normally

@NOTE: These tests *will* produce and consume AWS resources,
possibly incurring costs! Run sparingly and with care.
'''
