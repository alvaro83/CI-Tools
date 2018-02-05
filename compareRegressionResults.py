#!/usr/bin/env python

# author: Alvaro Gonzalez Arroyo
# email: <alvaro.g.arroyo@gmail.com>
# description: a basic script to compare results of several Jenkins executions

import urllib2
import argparse
import re
import os
import threading
import sys

from collections import defaultdict
from display.table import Table
from display.console_colors import color_ok, color_error
from display.unbuffered import Unbuffered

def main():
    parser = argparse.ArgumentParser(description="Show the test cases that fail in a local Jenkins job execution but pass in a reference Jenkins job execution")

    parser.add_argument("--local", required=True, nargs='+', help='Link to local jenkins jobs')
    parser.add_argument("--reference", required=True, help='Link to reference jenkins job')
    parser.add_argument("--both-fail", required=False, action='store_true',
                        help='With this option enabled, what the script shows are the test cases that fail simultaneously in both local and reference jobs')
    parser.add_argument("--color", required=False, action='store_true', help='Show results with beautiful colors')
    parser.add_argument("--compare", required=False, type=check_positive,
                        help='Number of previous executions to the reference one to compare with. Useful to see if there are unstable test cases')
    parser.add_argument("--test-suite", required=False, nargs='+', help='Test suite names to filter results')

    args = parser.parse_args()
    url_local = args.local
    url_ref = args.reference
    
    l = [['Test case']]
    
    row = 0
    col = 0
    tc_show = dict()
    
    local_check_status = ['FAILED', 'REGRESSION']
    ref_check_status = local_check_status if args.both_fail else ['PASSED', 'FIXED']
    
    reference = [set()]
    tcs_reference = [dict()]
    local = [set() for x in range(len(url_local))]
    tcs_local = [dict() for x in range(len(url_local))]
    i = 0
    
    def local_fetcher(i, lock):
        data_local = read_url(url)
        suites_local = get_suites(data_local)
        with lock:
            tcs_local[i] = get_all_tcs(suites_local)
            local[i] = set(tcs_local[i])
            l[0].append('Local status')
            
    def ref_fetcher():
        data_ref = read_url(url_ref)
        suites_ref = get_suites(data_ref)
        tcs_reference[0] = get_all_tcs(suites_ref)
        reference[0] = set(tcs_reference[0])
        
    lock = threading.Lock()
    threads = list()

    print 'Reading data from URLs ... ',
    t = threading.Thread(target=ref_fetcher)
    threads.append(t)
    t.start()
    for url in url_local:
        t = threading.Thread(target=local_fetcher, args=(i, lock))
        threads.append(t)
        t.start()
        col += 1
        i += 1
        
    for t in threads:
        t.join()

    print color_ok('DONE')

    tcs_reference = tcs_reference[0]
    reference = reference[0]

    i = 0
    print 'Comparing results ... ',
    for url in url_local:
        for key in local[i]:
            try:
                if (tcs_local[i][key] in local_check_status) and (tcs_reference[key] in ref_check_status):
                    tc_show, row, l = append_tc(key, tc_show, row, l, url_local, tcs_local, args.color, local_check_status)
            except KeyError:
                if tcs_local[i][key] in local_check_status:
                    tc_show, row, l = append_tc(key, tc_show, row, l, url_local, tcs_local, args.color, local_check_status)
        i += 1

    for key in tc_show.keys():
        try:
            if args.color:
                if tcs_reference[key] in local_check_status:
                    l[tc_show[key]][-1] = color_error(tcs_reference[key])
                else:
                    l[tc_show[key]][-1] = color_ok(tcs_reference[key])
            else:
                l[tc_show[key]][-1] = tcs_reference[key]
        except KeyError:
            l[tc_show[key]][-1] = ''

    l[0].append('Reference status')

    print color_ok('DONE')
    
    def comparer(i, lock):
        url_N = get_previous_N_url(url_ref, i)
        try:
            data_ref = read_url(url_N)
        except urllib2.HTTPError:
            return
        suites_ref = get_suites(data_ref)
        tcs_reference_N = get_all_tcs(suites_ref)
        for key in tc_show.keys():
            try:
                with lock:
                    if tcs_reference_N[key] in local_check_status:
                        tcs_comparison[key] += 1
                    tcs_total[key] += 1
            except KeyError:
                pass

    if args.compare:
        print 'Comparing with previous regressions ... ',
        tcs_comparison = dict.fromkeys(tc_show.keys(), 0)
        tcs_total = dict.fromkeys(tc_show.keys(), 0)

        lock = threading.Lock()
        threads = list()
        for i in range(1, args.compare+1):
            t = threading.Thread(target=comparer, args=(i, lock))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        l[0].append('#fail (total) in previous reference executions')

        for key in tc_show.keys():
            l[tc_show[key]].append(str(tcs_comparison[key]) + ' (' + str(tcs_total[key]) + ')')

        print color_ok('DONE')

    print 'Showing results ... '

    header = l[0]

    l.pop(0)

    if args.test_suite:
        l2 = [[]]
        for suite in args.test_suite:
            l2 += filter(lambda x: x[0].startswith(suite), l[1:])
    else:
        l2 = l

    l2.sort()
    l2.insert(0, header)

    try:
        cols = get_terminal_width()
        print Table(l2, [3*cols/7, cols/7, cols/7, 2*cols/7], spacing=True, count=True)
    except:
        print Table(l2, [0, 30, 40, 60], spacing=True, count=True)



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

def get_terminal_size():
    rows, cols = os.popen('stty size', 'r').read().split()
    return int(rows), int(cols)

def get_terminal_width():
    rows, cols = get_terminal_size()
    return cols


if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)
    main()
    exit(0)
