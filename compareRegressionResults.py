#!/usr/bin/env python

# author: Alvaro Gonzalez Arroyo
# email: <alvaro.g.arroyo@gmail.com>
# description: a basic script to compare results of several Jenkins executions

import urllib2
import argparse
import re

from collections import defaultdict
from display.table import Table
from display.console_colors import color_ok, color_error

def main():
    parser = argparse.ArgumentParser(description="Show the test cases that fail in a local Jenkins job execution but pass in a reference Jenkins job execution")

    parser.add_argument("--local", required=True, nargs='+', help='Link to local jenkins jobs')
    parser.add_argument("--reference", required=True, help='Link to reference jenkins job')
    parser.add_argument("--both-fail", required=False, action='store_true',
                        help='With this option enabled, what the script shows are the test cases that fail simultaneously in both local and reference jobs')
    parser.add_argument("--color", required=False, action='store_true', help='Show results with beautiful colors')
    parser.add_argument("--compare", required=False, type=check_positive,
                        help='Number of previous executions to the reference one to compare with. Useful to see if there are unstable test cases')

    args = parser.parse_args()
    url_local = args.local
    url_ref = args.reference

    print 'Reading data for reference URL ... ',

    data_ref = read_url(url_ref)
    suites_ref = get_suites(data_ref)
    tcs_reference = get_all_tcs(suites_ref)
    reference = set(tcs_reference)

    print color_ok('DONE')

    l = [['Test case']]

    row = 0
    col = 0
    tc_show = dict()

    local_check_status = ['FAILED', 'REGRESSION']
    ref_check_status = local_check_status if args.both_fail else ['PASSED', 'FIXED']

    local = [set() for x in range(len(url_local))]
    tcs_local = [dict() for x in range(len(url_local))]
    i = 0

    for url in url_local:
        print 'Reading data for local URL ... ',
        col += 1
        l[0].append('Local status')
        data_local = read_url(url)
        suites_local = get_suites(data_local)
        tcs_local[i] = get_all_tcs(suites_local)

        local[i] = set(tcs_local[i])
        i += 1

        print color_ok('DONE')

    i = 0
    print 'Comparing results ... ',
    for url in url_local:
        for key in reference.intersection(local[i]):
            if (tcs_local[i][key] in local_check_status) and (tcs_reference[key] in ref_check_status):
                if key not in tc_show.keys():
                    row += 1
                    tc_show[key] = row
                    l.extend([['']* (2+len(url_local))]) #['Test case', N*'Local status', 'Reference status']
                    l[row][0] = key
                for k in range(len(url_local)):
                    l[row][k+1] = tcs_local[k].get(key, '')
                    if args.color:
                        if l[row][k+1] in local_check_status:
                            l[row][k+1] = color_error(l[row][k+1])
                        else:
                            l[row][k+1] = color_ok(l[row][k+1])
        i += 1

    for key in tc_show.keys():
        if args.color:
            if tcs_reference[key] in local_check_status:
                l[tc_show[key]][-1] = color_error(tcs_reference[key])
            else:
                l[tc_show[key]][-1] = color_ok(tcs_reference[key])
        else:
            l[tc_show[key]][-1] = tcs_reference[key]

    l[0].append('Reference status')

    print color_ok('DONE')

    if args.compare:
        print 'Comparing with previous regressions ... ',
        tcs_comparison = dict.fromkeys(tc_show.keys(), 0)
        tcs_total = dict.fromkeys(tc_show.keys(), 0)
        for i in range(1, args.compare+1):
            url_N = get_previous_N_url(url_ref, i)
            try:
                data_ref = read_url(url_N)
            except urllib2.HTTPError:
                continue
            suites_ref = get_suites(data_ref)
            tcs_reference_N = get_all_tcs(suites_ref)
            for key in tc_show.keys():
                try:
                    if tcs_reference_N[key] in local_check_status:
                        tcs_comparison[key] += 1
                    tcs_total[key] += 1
                except KeyError:
                    pass

        l[0].append('#fail (total) in previous reference executions')

        for key in tc_show.keys():
            l[tc_show[key]].append(str(tcs_comparison[key]) + ' (' + str(tcs_total[key]) + ')')

        print color_ok('DONE')

    print 'Showing results ... '

    print Table(l, [0, 30, 40, 40], spacing=True, count=True)



def read_url(url):
    '''
    Read data in JSON format from URL and returns it as a dictionary
    :param url: URL to read data from
    :type url: str
    :return: data readen from URL
    :rtype: dict
    '''
    if not url.endswith('/testReport/api/python') and not url.endswith('/testReport/api/python/'):
        url += '/testReport/api/python'
    response = urllib2.urlopen(url)
    return eval(response.read())

def get_suites(data):
    '''
    Get all test suites from input dictionary data
    :param data: data to be parsed
    :type data: dict
    :return: test suites information
    :rtype: dict
    '''
    return data.get('suites', [])

def get_all_tcs(suites):
    '''
    Parse input test suites to get all test cases in form of dictionary with key:value
    test_suite_name.test_case_name : status, where status will be typically 'FAILED', 'REGRESSION', 'PASSED', 'FIXED'
    :param suites: test suites to be parsed
    :type suites: dict
    :return: test cases
    :rtype: dict
    '''
    tcs = dict()
    for suite in suites:
        tcs_per_suite = suite.get('cases')
        for tc in tcs_per_suite:
            tcs.update({tc['className'] + '.' + tc['name']: tc['status']})
    return tcs

def check_positive(value):
    '''
    To be used as argument parser to check if input parameter is a positive integer
    :param value: input parameter
    :type value: str
    :return: int(value)
    :rtype: int
    '''
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" %value)
    return ivalue

def get_previous_N_url(url, N):
    '''
    URL finished with a number, typically a Jenkins job execution,
    is calculated the URL corresponding to the previous N execution
    :param url: URL from where to calculate the previous N one
    :type url: str
    :param N: N previos execution
    :type N: str
    :return: corresponding URL of the previous N build
    :rtype: str
    '''
    if url.endswith('/testReport/api/python') or url.endswith('/testReport/api/python/'):
        url = re.sub('\/testReport/api/python', '', url)
    if url.endswith('/'):
        url = url[0:len(url)-1]
    l = url.rsplit('/')
    j = l[-1]
    url = '/'.join(l[0:len(l)-1]) + '/' + str(int(j)-int(N))
    return url


if __name__ == "__main__":
    main()
    exit(0)
