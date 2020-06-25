
# Copyright (c) 2017, George Haoran Wang georgewhr@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import re
import sys
import os
import pycurl, json
import io
import argparse
import json
import yaml
import datetime
import time
import multiprocessing
import io
from multiprocessing import Value, Lock, Manager
from tabulate import tabulate
from bs4 import BeautifulSoup
import certifi

CPU_CORES = multiprocessing.cpu_count()

def cmdArgumentParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--batch', required=True, type=int, help='Batch Number')
	parser.add_argument('-c', '--case_num', required=True, type=str, help='Case Number')
	parser.add_argument('-v', '--verbose', action="store_true", help='Verbose mode will print out more information')
	parser.add_argument("--dryrun", action="store_true", help='dryrun')
	return parser.parse_args()

def get_result(case_num,prefix,verbose):
	info = {}
	result=''
	buf = io.BytesIO()
	url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
	case_num = prefix + str(case_num)
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.POSTFIELDS, 'appReceiptNum=%s'%case_num)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()

	soup = BeautifulSoup(buf.getvalue(),"html.parser")
	mycase_txt = soup.findAll("div", { "class" : "rows text-center" })

	for i in mycase_txt:
		result=result+i.text

	result = result.split('\n')
	buf.close()
	try:
		details = result[2].split(',')
		recv_date = get_case_receive_date(details)
		case_type = get_case_type(result[2])
		info[case_num] = {}
		info[case_num]['Type'] = case_type
		info[case_num]['Status'] = result[1]
		info[case_num]['Received'] = recv_date

		if verbose:
			print(info)

	except Exception as e:
		print('USCIS format is incorrect')

	return info

def get_batch_pair(total_num,case_s,case_e):
	batch = {}
	info = []
	for i in range(total_num // CPU_CORES):
		s = CPU_CORES * i + case_s
		e = s + CPU_CORES - 1
		batch = {
			"start":s,
			"end": e
		}
		info.append(batch)
	return info

def query_website(ns,batch_result,prefix,lock,verbose):
	local_result = []
	if verbose:
		print('s is %d, e is %d'%(int(batch_result['start']),int(batch_result['end'])))
	for case_n in range(int(batch_result['start']),int(batch_result['end'])):
		local_result.append(get_result(case_n,prefix,verbose))

	lock.acquire()
	ns.df = ns.df + local_result
	lock.release()
	time.sleep(1)

def get_case_type(line):

	iCase = re.search("\w*I-\w*", line)
	crCase = re.search("\w*CR-\w*", line)
	irCase = re.search("\w*IR-\w*", line)

	if iCase:
		return iCase.group(0)
	elif crCase:
		return crCase.group(0)
	elif irCase:
		return irCase.group(0)
	else:
		return 'None Case'

def get_case_receive_date(details):
	year = str(details[1][1:])

	if year.isdigit():
		recv_date = details[0][3:] + ' ' + details[1][1:]
	else:
		recv_date = None

	return recv_date

def main():
	final_result = []
	reminder_result = []
	args = cmdArgumentParser()
	case_numberic = int(args.case_num[3:])
	prefix = args.case_num[:3]
	lock = Lock()
	jobs = []
	mgr = Manager()
	ns = mgr.Namespace()
	ns.df = final_result

	start = case_numberic - args.batch
	end = case_numberic + args.batch

	total_num = end - start + 1
	rmnder = total_num % CPU_CORES

	if total_num > 20:
		batch_result = get_batch_pair(total_num,start,end)

		for i in range(len(batch_result)):
			p = multiprocessing.Process(target=query_website,args=(ns,batch_result[i],prefix,lock,args.verbose,))
			jobs.append(p)
			p.start()
		for job in jobs:
			job.join()

		final_result = ns.df

		# for i in range(end - rmnder + 1,end):
		# 	reminder_result.append(get_result(i,prefix))
	else:
		for i in range(start,end):
			final_result.append(get_result(i,prefix,args.verbose))

	json_type = json.dumps(final_result,indent=4)
	now = datetime.datetime.now()
	with open('data-%s.yml'%now.strftime("%Y-%m-%d"), 'w') as outfile:
		yaml.dump(yaml.load(json_type, Loader=yaml.BaseLoader), outfile, allow_unicode=True)
	print(yaml.dump(yaml.load(json_type, Loader=yaml.BaseLoader), allow_unicode=True))

if __name__ == "__main__":
	main()
