# CI-Tools
Continuous Integration tools

A good continuous integration system should be stable and none test case in the regression should never fail. However, in some cases
there are tests that are unstable. It is crutial that changes done by anyone do not add new instabilities or failing test cases when
adding new features. This repository aims to have different tools to secure this goal.

## Installation

First, install the related Python libraries:

  $ setup.py install --user --prefix=

If installation is successful, you can now run any of the tools.

## Tools

At the moment, only one tool is available.

### compareRegressionResults.py

This scripts allow to automatically compare the results of a regression run in a local branch againts the reference regression.

    $ compareRegressionResults.py -h
     usage: compareRegressionResults.py [-h] --local LOCAL [LOCAL ...] --reference
                                    REFERENCE [--both-fail] [--color]
     
     Show the test cases that fail in a local Jenkins job execution but pass in a
     reference Jenkins job execution
     
     optional arguments:
       -h, --help            show this help message and exit
       --local LOCAL [LOCAL ...]
                             Link to local jenkins jobs
       --reference REFERENCE
                             Link to reference jenkins job
       --both-fail           With this option enabled, what the script shows are
                             the test cases that fail simultaneously in both local
                             and reference jobs
       --color               Show results with beautiful colors
       
Example of usage:

    $ compareRegressionResults.py \
    --local https://myjenkinsserver/job/localjob/6/ \
    --reference https://myjenkinsserver/job/referencejob/55/
    
    +-------------------------------+--------------+------------------+
    | Test case                     | Local status | Reference status |
    +-------------------------------+--------------+------------------+
    | test_suite_001.test_case_023  | FAILED       | PASSED           |
    |                               |              |                  |
    | test_suite_007.test_case_092  | FAILED       | PASSED           |
    |                               |              |                  |
    | test_suite_103.test_case_005  | REGRESSION   | PASSED           |
    |                               |              |                  |
    +-------------------------------+--------------+------------------+
    | #elements: 3                                                    |
    +-------------------------------+--------------+------------------+

The local argument admits a list of jobs, so we can compare simultaneously some local executions to a reference execution.
It will show the test cases that have fail in any or both of the local executions but have passed in the reference one:

    $ compareRegressionResults.py \
    --local https://myjenkinsserver/job/localjob/6/ \
            https://myjenkinsserver/job/localjob/7/ \
    --reference https://myjenkinsserver/job/referencejob/55/
    
    +------------------------------+--------------+--------------+-----------------+
    | Test case                    | Local status | Local status |Reference status |
    +------------------------------+--------------+--------------+-----------------+
    | test_suite_001.test_case_023 | FAILED       | FIXED        | PASSED          |
    |                              |              |              |                 |
    | test_suite_007.test_case_092 | FAILED       | FIXED        | PASSED          |
    |                              |              |              |                 |
    | test_suite_103.test_case_005 | REGRESSION   | FIXED        | PASSED          |
    |                              |              |              |                 |
    | test_suite_103.test_case_008 | PASSED       | REGRESSION   | PASSED          |
    |                              |              |              |                 |
    +------------------------------+--------------+--------------+-----------------+
    | #elements: 4                                                                 |
    +------------------------------+--------------+--------------+-----------------+
    
The --color option shows the results with beautiful color formatting to make visualization easier.

It is possible to compare with a customized number of reference jobs. When the option --compare is enabled, the script still
shows the test cases that have failed in the local job(s) but have passed in the one indicated as reference, but a new column
shows the number of times that these test cases have failed in the previous N reference executions.

    $ compareRegressionResults.py \
    --local https://myjenkinsserver/job/localjob/6/ \
    --reference https://myjenkinsserver/job/referencejob/55/
    --compare 10
    
    +-------------------------------+--------------+------------------+---------------+
    | Test case                     | Local status | Reference status | #fail (total) |
    +-------------------------------+--------------+------------------+---------------+
    | test_suite_001.test_case_023  | FAILED       | PASSED           | 6 (8)         |
    |                               |              |                  |               |
    | test_suite_007.test_case_092  | FAILED       | PASSED           | 0 (10)        |
    |                               |              |                  |               |
    | test_suite_103.test_case_005  | REGRESSION   | PASSED           | 0 (10)        |
    |                               |              |                  |               |
    +-------------------------------+--------------+------------------+---------------+
    | #elements: 3                                                    |               |
    +-------------------------------+--------------+------------------+---------------+
    
This indicates that the first test case has failed 6 out 8 times in the reference job, thus it is an unstable test case.
