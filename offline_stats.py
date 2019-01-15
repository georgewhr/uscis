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
from sklearn.linear_model import LogisticRegression


def cmdArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name', required=False, type=str, help='File Name')
    parser.add_argument('-c', '--case_num', required=True, type=str, help='Case Number')
    parser.add_argument("--dryrun", action="store_true", help='dryrun')
    return parser.parse_args()


def get_dummy_status(status):
    if status in [
        'Card Was Mailed To Me', 'New Card Is Being Produced',
        'Card Was Picked Up By The United States Postal Service',
        'Card Was Delivered To Me By The Post Office'
    ]:
        return 1
    elif status in [
        'Case Was Received',
        'Correspondence Was Received And USCIS Is Reviewing It',
        'Fees Were Waived', 'Fingerprint Fee Was Received',
        'Request for Initial Evidence Was Mailed', 'Name Was Updated',
        'Date of Birth Was Updated',
        'Notice Explaining USCIS Actions Was Mailed',
        'Duplicate Notice Was Mailed', 'Case Is Pending at a Local Office'
    ]:
        return 0
    else:
        return None


def main():
    now = datetime.datetime.now()
    args = cmdArgumentParser()
    file = args.file_name or 'data-' + now.strftime("%Y-%m-%d")
    case = int(args.case_num[3:])
    d = {}
    with open(file + '.yml', 'r') as f:
        doc = yaml.load(f)

        for i in doc:
            d.update(i)

    df = pd.DataFrame(d).T.sort_index()
    df['Status'] = df['Status'].apply(get_dummy_status)
    df['Number'] = df.index.str.slice(start=3).astype(int)
    df = df.loc[df['Type'] == 'I-765'].dropna()
    df.to_csv(file + '.csv')

    model = LogisticRegression()
    _ = model.fit(df[['Number']], df['Status'] == 1)
    print(model.predict_proba(case)[0][1])


if __name__ == "__main__":
    main()
