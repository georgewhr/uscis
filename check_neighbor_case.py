
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
from tabulate import tabulate
from bs4 import BeautifulSoup

def cmdArgumentParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--batch', required=True, type=int, help='Batch Number')
	parser.add_argument('-c', '--case_num', required=True, type=str, help='Case Number')
	args = parser.parse_args()
	return parser.parse_args()

def get_result(case_num):
	info = {}
	result=''
	buf = cStringIO.StringIO()
	url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
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


	details = result[2].split(',')
	recv_date = details[0][3:] + ' ' + details[1][1:]
	case_type = details[2].split(' ')[-1]
	info = {
		"Type": case_type,
		"Received": recv_date,
		"Number": case_num,
		"Status": result[1]
	}

	return info

def main():
	args = cmdArgumentParser()
	case_numberic = int(args.case_num[3:])
	prefix = args.case_num[:3]
	final_result = []
	# print '%d'%num

	start = case_numberic - args.batch
	end = case_numberic + args.batch

	for i in range(start,end):
		case_n = prefix+str(i)
		# print case_n
		final_result.append(get_result(case_n))

	json_type = json.dumps(final_result,indent=4)
	with open('data.yml', 'w') as outfile:
		yaml.dump(yaml.load(json_type), outfile, allow_unicode=True)
	# print yaml.dump(yaml.load(json_type), allow_unicode=True)

if __name__ == "__main__":
	main()
