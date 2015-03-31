'''Lambda integration tests.

To run, you will need the following:

  - AWS credentials and region defined in ~/.aws/credentials
  - A default execution role specified in ~/.aws/lambda.yml
  - `lfm` on your path or set up as a bash alias (commands
    are run in subprocesses) -- to verify, make sure `lfm -h`
    produces output in your shell

@NOTE: These tests *will* produce and consume AWS resources,
possibly incurring costs! Run sparingly and with care.
'''
