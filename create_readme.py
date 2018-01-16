#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 创建 readme 的脚本
"""
import os
import re
from itertools import dropwhile

__author__ = '__L1n__w@tch'

PATH_RE = re.compile("\((.*)\)")


def run(md_path):
    """
    读取 SUMMARY.md 并生成对应目录
    :param md_path:
    :return:
    """
    with open(md_path) as f:
        data = f.readlines()

    data = data[3:]
    for each_line in data:
        each_line = each_line.strip()

        result = PATH_RE.findall(each_line)[0]
        path, name = os.path.dirname(result), os.path.basename(result)
        os.makedirs(path, exist_ok=True)
        with open(result, "w") as f:
            pass


if __name__ == "__main__":
    summary_md = "/Users/L1n/Desktop/Code/Python/Flask-Web-Python-Web-/SUMMARY.md"

    run(summary_md)
