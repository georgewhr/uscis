
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
import cStringIO
import argparse
import json
import yaml
import time
import multiprocessing
import io
from multiprocessing import Value, Lock, Manager
from tabulate import tabulate
from bs4 import BeautifulSoup

CPU_CORES = 16

def cmdArgumentParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--batch', required=True, type=int, help='Batch Number')
	parser.add_argument('-c', '--case_num', required=True, type=str, help='Case Number')
	parser.add_argument('-v', '--verbose', action="store_true", help='Verbose mode will print out more information')
	parser.add_argument("--dryrun", action="store_true", help='dryrun')
	args = parser.parse_args()
	return parser.parse_args()

def get_result(case_num,prefix,verbose):
	info = {}
	result=''
	buf = cStringIO.StringIO()
	url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
	case_num = prefix + str(case_num)
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.POSTFIELDS, 'appReceiptNum=%s'%case_num)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	soup = BeautifulSoup(buf.getvalue(),"html.parser")
	mycase_txt = soup.findAll("div", { "class" : "rows text-center" })

	for i in mycase_txt:
		result=result+i.text

	result = result.split('\n')
	buf.close()
	try:
		details = result[2].split(',')
		recv_date = details[0][3:] + ' ' + details[1][1:]
		case_type = details[2].split(' ')[-1]
		info = {
			"Type": case_type,
			"Received": recv_date,
			"Number": case_num,
			"Status": result[1]
		}
		if verbose:
			print info

	except Exception as e:
		print 'USCIS format is incorrect'

	return info

def get_batch_pair(total_num,case_s,case_e):
	batch = {}
	info = []
	for i in range(total_num / CPU_CORES):
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
		print 's is %d, e is %d'%(int(batch_result['start']),int(batch_result['end']))
	for case_n in range(int(batch_result['start']),int(batch_result['end'])):
		local_result.append(get_result(case_n,prefix,verbose))

	lock.acquire()
	ns.df = ns.df + local_result
	lock.release()
	time.sleep(1)

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
	with open('data.yml', 'w') as outfile:
		yaml.dump(yaml.load(json_type), outfile, allow_unicode=True)
	print yaml.dump(yaml.load(json_type), allow_unicode=True)

if __name__ == "__main__":
	main()
