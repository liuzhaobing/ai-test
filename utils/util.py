# -*- coding:utf-8 -*-
import os
import re
import time
import math
import base64
import logging
from pathlib import Path

import yaml
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures
from typing import Callable
from multiprocessing.pool import ThreadPool

from main import LOG_DIR, BASE_DIR


def process_nan(content):
    if isinstance(content, float):
        if math.isnan(content):
            return ""
    return content


def save_file_from_http(url):
    filename = f"{mock_job_instance_id()}_{url.split('/')[-1]}"
    new_filepath = os.path.join(LOG_DIR, "file", filename)
    Path(new_filepath).parent.mkdir(parents=True, exist_ok=True)

    try:
        res = requests.get(url, stream=True)
        with open(new_filepath, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return os.path.relpath(new_filepath, BASE_DIR)
    except Exception as e:
        logging.error(f"save_file_from_http error: {e}")
        return None


def mock_job_instance_id():
    return f'{time_strf_now()}{base64.b32encode(os.urandom(5)).decode("ascii")}'


def mock_trace_id():
    return f'L{mock_job_instance_id()}@cloudminds-test.com.cn'


def time_strf_now():
    """返回当前时间格式"""
    return time.strftime("%Y%m%d%H%M%S")


def runner(function: Callable, work_items, threads: int = 5, time_out: int = 30, show_progress: bool = True):
    """多线程执行任务
    :param function: 调用的方法
    :param work_items: 列表数据
    :param threads: 并发数
    :param time_out: 单个并发超时时长控制
    :param show_progress: 是否显示进度条
    :return:
    """

    def worker_thread(*args, **kwargs):
        """
        Worker thread for evaluating a single sample.
        """
        while True:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(function, *args, **kwargs)
            try:
                future.done()
                result = future.result(timeout=time_out)
                return result
            except concurrent.futures.TimeoutError as e:
                executor.shutdown(wait=False)
                logging.info(f"wait future.result timeout [{time_out}] {e}")
                # return None

    with ThreadPool(threads) as pool:
        logging.info(f"Running in threaded mode with {threads} threads!")
        iter = pool.imap(worker_thread, work_items)
        idx_and_result = list(tqdm(iter, total=len(work_items), disable=not show_progress))
    return idx_and_result


def list_duplicate_removal(input_list):
    output_list = []
    [output_list.append(v) for v in input_list if v not in output_list]
    return output_list


def load_data_from_xlsx(filename: str, sheet_name: str, **kwargs) -> list[dict]:
    df = pd.read_excel(io=filename, sheet_name=sheet_name, **kwargs)
    return [dict(zip(list(df.columns), line)) for line in df.values]


def save_data_to_xlsx(data: list[dict], filename: str, **kwargs):
    logging.info(f"Logged {len(data)} rows of data to {filename}")
    return pd.DataFrame(data).to_excel(excel_writer=filename, index=False, **kwargs)


def check_grpc_url(address: str) -> bool:
    pattern = re.compile(r"^(?:(?:\d{1,3}\.){3}\d{1,3}|[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+):\d{1,5}$")
    return True if pattern.match(address) else False


def check_http_url(address: str) -> bool:
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return True if pattern.match(address) else False


def load_data_from_yaml(filename: str):
    return yaml.load(open(filename, "r", encoding="UTF-8"), Loader=yaml.FullLoader)


def read_files(dir_name: str, allow_suffix: str = ".jsonl"):
    files = []
    if os.path.isfile(dir_name):
        return [dir_name]
    for dir_path, dir_names, filenames in os.walk(dir_name):
        for filepath in filenames:
            file_full_path = os.path.join(dir_path, filepath)
            if file_full_path.endswith(allow_suffix):
                files.append(file_full_path)
    return files


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)
