
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
from tabulate import tabulate
from bs4 import BeautifulSoup

def cmdArgumentParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--batch', required=True, type=int, help='Batch Number')
	parser.add_argument('-c', '--case_num', required=True, type=str, help='Case Number')
	args = parser.parse_args()
	return parser.parse_args()

def get_result(case_num):
	pair=[]
	result=''
	buf = cStringIO.StringIO()
	url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.POSTFIELDS, 'appReceiptNum=%s'%case_num)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	soup = BeautifulSoup(buf.getvalue(),"html.parser")
	# mycase_status = soup.findAll("div", { "class" : "current-status-sec" })
	mycase_txt = soup.findAll("div", { "class" : "rows text-center" })

	for i in mycase_txt:
		result=result+i.text

	result = result.split('\n')
	buf.close()

	pair.append(case_num)
	pair.append(result[1])

	return pair

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

	print tabulate(sorted(final_result,key=lambda x: x[0]),headers=['Case Number', 'Status'])

	# print final_result
	# print tabulate(sorted(final_result,key=lambda l:l[2]), headers=['Service', 'Version'])


if __name__ == "__main__":
	main()
