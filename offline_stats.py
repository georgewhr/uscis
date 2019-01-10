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
import pycurl
import json
import argparse
import json
import yaml
import time
import datetime
import multiprocessing
import io
import sys
from multiprocessing import Value, Lock, Manager
from tabulate import tabulate
from bs4 import BeautifulSoup
import pandas as pd


def main():
    now = datetime.datetime.now()

    d = {}
    with open('data-' + now.strftime("%Y-%m-%d") + '.yml', 'r') as f:
        doc = yaml.load(f)

        for i in doc:
            d.update(i)

    df = pd.DataFrame(d).T
    print(df['Status'].value_counts())


if __name__ == "__main__":
    main()
