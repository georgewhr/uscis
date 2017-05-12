
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
import datetime
import multiprocessing
import io
from multiprocessing import Value, Lock, Manager
from tabulate import tabulate
from bs4 import BeautifulSoup


def main():
	now = datetime.datetime.now()
	print now.strftime("%Y-%m-%d")
	exit(0)
	with open('data.yml', 'r') as f:
		doc = yaml.load(f)

	for i in doc:
		if 'Case Was Received' not in i['Status']:
			print i

if __name__ == "__main__":
	main()
