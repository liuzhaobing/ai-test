# -*- coding:utf-8 -*-
"""
This file defines utilities for working with data and files of various types.
"""
import csv
import dataclasses
import gzip
import itertools
import base64
import datetime
import json
import logging
import re
import typing as t
import os
import warnings
from collections.abc import Iterator
from functools import partial
from typing import Any, Sequence, Union

import blobfile as bf
import lz4.frame
import pydantic
import pyzstd
import yaml
import pandas as pd
from openpyxl import Workbook
from datasets import load_dataset, get_dataset_config_names


def get_all_datasets(dataset: str) -> t.Dict:
    data = {}
    names = get_dataset_config_names(dataset)
    for name in names:
        if name not in data:
            data[name] = {}
        dataset = load_dataset(dataset, name=name)
        splits = dataset.keys()
        for _, split in enumerate(splits):
            rows = dataset[split].to_list()
            data[name][split] = rows
    return data


def check_grpc_url(address: str) -> bool:
    return True
    pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}\:\d{1,5}$")
    return True if pattern.match(address) else False


def check_http_url(address: str) -> bool:
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return True if pattern.match(address) else False


def gzip_open(filename: str, mode: str = "rb", openhook: Any = open) -> gzip.GzipFile:
    """Wrap the given openhook in gzip."""
    if mode and "b" not in mode:
        mode += "b"

    return gzip.GzipFile(fileobj=openhook(filename, mode), mode=mode)


def lz4_open(filename: str, mode: str = "rb", openhook: Any = open) -> lz4.frame.LZ4FrameFile:
    if mode and "b" not in mode:
        mode += "b"

    return lz4.frame.LZ4FrameFile(openhook(filename, mode), mode=mode)


def zstd_open(filename: str, mode: str = "rb", openhook: Any = open) -> pyzstd.ZstdFile:
    if mode and "b" not in mode:
        mode += "b"

    return pyzstd.ZstdFile(openhook(filename, mode), mode=mode)


def open_by_file_pattern(filename: str, mode: str = "r", **kwargs: Any) -> Any:
    """Can read/write to files on gcs/local with or without gzipping. If file
    is stored on gcs, streams with blobfile. Otherwise use vanilla python open. If
    filename endswith gz, then zip/unzip contents on the fly (note that gcs paths and
    gzip are compatible)"""
    open_fn = partial(bf.BlobFile, **kwargs)
    try:
        if filename.endswith(".gz"):
            return gzip_open(filename, openhook=open_fn, mode=mode)
        elif filename.endswith(".lz4"):
            return lz4_open(filename, openhook=open_fn, mode=mode)
        elif filename.endswith(".zst"):
            return zstd_open(filename, openhook=open_fn, mode=mode)
        else:
            return open_fn(filename, mode=mode)
    except Exception as e:
        raise RuntimeError(f"Failed to open: {filename}") from e


def _get_jsonl_file(path):
    logging.info(f"Fetching {path}")
    with open_by_file_pattern(path, mode="r") as f:
        return list(map(json.loads, f.readlines()))


def _get_json_file(path):
    logging.info(f"Fetching {path}")
    with open_by_file_pattern(path, mode="r") as f:
        return json.loads(f.read())


def _stream_jsonl_file(path) -> Iterator:
    logging.info(f"Streaming {path}")
    with bf.BlobFile(path, "r", streaming=True) as f:
        for line in f:
            yield json.loads(line)


def get_lines(path) -> list[dict]:
    """
    Get a list of lines from a file.
    """
    with open_by_file_pattern(path, mode="r") as f:
        return f.readlines()


def get_jsonl(path: str) -> list[dict]:
    """
    Extract json lines from the given path.
    If the path is a directory, look in subpaths recursively.

    Return all lines from all jsonl files as a single list.
    """
    if bf.isdir(path):
        result = []
        for filename in bf.listdir(path):
            if filename.endswith(".jsonl"):
                result += get_jsonl(os.path.join(path, filename))
        return result
    return _get_jsonl_file(path)


def get_jsonls(paths: Sequence[str], line_limit=None) -> list[dict]:
    return list(iter_jsonls(paths, line_limit))


def get_json(path) -> dict:
    if bf.isdir(path):
        raise ValueError("Path is a directory, only files are supported")
    return _get_json_file(path)


def iter_jsonls(paths: Union[str, list[str]], line_limit=None) -> Iterator[dict]:
    """
    For each path in the input, iterate over the jsonl files in that path.
    Look in subdirectories recursively.

    Use an iterator to conserve memory.
    """
    if type(paths) == str:
        paths = [paths]

    def _iter():
        for path in paths:
            if bf.isdir(path):
                for filename in bf.listdir(path):
                    if filename.endswith(".jsonl"):
                        yield from iter_jsonls([os.path.join(path, filename)])
            else:
                yield from _stream_jsonl_file(path)

    return itertools.islice(_iter(), line_limit)


def get_csv(path, fieldnames=None):
    with bf.BlobFile(path, "r", cache_dir="/tmp/bf_cache", streaming=False) as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        return [row for row in reader]


def _to_py_types(o: Any) -> Any:
    if isinstance(o, dict):
        return {k: _to_py_types(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_to_py_types(v) for v in o]

    if dataclasses.is_dataclass(o):
        return _to_py_types(dataclasses.asdict(o))

    # pydantic data classes
    if isinstance(o, pydantic.BaseModel):
        return json.loads(o.json())

    return o


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> str:
        return _to_py_types(o)


def jsondumps(o: Any, ensure_ascii: bool = False, **kwargs: Any) -> str:
    return json.dumps(o, cls=EnhancedJSONEncoder, ensure_ascii=ensure_ascii, **kwargs)


def jsondump(o: Any, fp: Any, ensure_ascii: bool = False, **kwargs: Any) -> None:
    json.dump(o, fp, cls=EnhancedJSONEncoder, ensure_ascii=ensure_ascii, **kwargs)


def jsonloads(s: str, **kwargs: Any) -> Any:
    return json.loads(s, **kwargs)


def jsonload(fp: Any, **kwargs: Any) -> Any:
    return json.load(fp, **kwargs)


def fill_nan(df: pd.DataFrame, value: t.Any = "", **kwargs) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        df.fillna(value, inplace=True, **kwargs)
    return df


def generate_job_instance_id(tp: str = "LLM"):
    now = datetime.datetime.now()
    return tp.upper() + now.strftime("%Y%m%d%H%M%S") + base64.b32encode(os.urandom(5)).decode("ascii")


def generate_trace_id(tp: str = "LLM"):
    return generate_job_instance_id(tp) + "_myroki_test_com"


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        logging.info(f"Reading yaml file {file_path}")
        return yaml.safe_load(file)


def format_log_details(headers: list[dict], datas: list[dict]):
    """
    headers = [{"key": "id", "label": "用例编号"}, {"key": "question", "label": "测试语句"},
               {"key": "domain", "label": "期望domain"}, {"key": "act_domain", "label": "实际domain"},
               {"key": "intent", "label": "期望intent"}, {"key": "act_intent", "label": "实际intent"},
               {"key": "is_intent_pass", "label": "意图是否通过"}, {"key": "slots", "label": "槽位期望值"},
               {"key": "act_slots", "label": "槽位实际值"}, {"key": "is_slots_pass", "label": "槽位是否通过"},
               {"key": "is_pass", "label": "是否通过"}, {"key": "edg_cost", "label": "端侧耗时(ms)"},
               {"key": "answer_string", "label": "回答内容"}, {"key": "device_id", "label": "DeviceId"},
               {"key": "session_id", "label": "SessionId"}, {"key": "trace_id", "label": "TranceId"}]
    datas = [
        {"id": 1, "question": "今天下雨吗", "domain": "weather", "act_domain": "weather", "intent": "GetWeather",
         "act_intent": "GetWeather", "is_intent_pass": True, "slots": "{\"日期\":\"今天\"}",
         "act_slots": "{\"日期\":\"今天\"}", "is_slots_pass": True,
         "is_pass": True, "edg_cost": 0, "answer_string": "今天天气晴朗", "device_id": "123456789",
         "session_id": "123456789", "trace_id": "123456789"},
        {"id": 2, "question": "明天下雨吗", "domain": "weather", "act_domain": "weather", "intent": "GetWeather",
         "act_intent": "GetWeather", "is_intent_pass": True, "slots": "{\"日期\":\"明天\"}",
         "act_slots": "{\"日期\":\"明天\"}", "is_slots_pass": True,
         "is_pass": True, "edg_cost": 0, "answer_string": "明天天气晴朗", "device_id": "123456789",
         "session_id": "123456789", "trace_id": "123456789"},
    ]
    :param headers:
    :param datas:
    :return:
    """
    return [[h["label"] for h in headers]] + [[data.get(header["key"], "") for header in headers] for data in datas]


def write_excel_file(filename: str, **kwargs):
    wb = Workbook()
    wb.remove(wb["Sheet"])
    for key, values in kwargs.items():
        ws = wb.create_sheet(key)
        for row in values:
            for index, item in enumerate(row):
                if isinstance(item, (list, dict)):
                    row[index] = json.dumps(item, ensure_ascii=False)
            try:
                ws.append(row)
            except Exception as e:
                logging.warning(e)
    wb.save(filename)
    logging.info(f"Excel file {filename} created")
    return filename


def write_json_file(filename: str, data: list[dict]):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({row["trace_id"]: row for row in data}, f, indent=4, ensure_ascii=False)
    return filename


def load_data_from_xlsx(filename: str, sheet_name: str, **kwargs) -> list[dict]:
    """从excel中读取数据为JSON格式的对象
    Parameters
    ----------

    filename : str
        /home/download/xxx.xlsx
    sheet_name : str
        Sheet1

        | id   | text_1                    | text_2                 |
        | ---- | ------------------ ------ | --------------------- |
        | 1    | 后面的那几个机器人是你的朋友吗 | 后面的机器人是你的朋友吗   |
        | 2    | 后面的那几个机器人是你的朋友吗 | 你的机器人朋友是谁       |
        | 3    | 后面的那几个机器人是你的朋友吗 | 那坏人是你的朋友吗       |
        | 4    | 后面的那几个机器人是你的朋友吗 | 你们的朋友都是机器人吗   |

    Returns
    -------
    list[dict]
        [{"id": 1, "text_1": "后面的那几个机器人是你的朋友吗", "text_2": "后面的机器人是你的朋友吗"},
         {"id": 2, "text_1": "后面的那几个机器人是你的朋友吗", "text_2": "你的机器人朋友是谁"},
         {"id": 3, "text_1": "后面的那几个机器人是你的朋友吗", "text_2": "那坏人是你的朋友吗"},
         {"id": 4, "text_1": "后面的那几个机器人是你的朋友吗", "text_2": "你们的朋友都是机器人吗"}]
    """
    df = pd.read_excel(io=filename, sheet_name=sheet_name, **kwargs)
    df = fill_nan(df)
    return df.to_dict(orient="records")


def extract_output_json(content: str) -> dict:
    def try_load_json(string: str) -> dict:
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            return {}

    def try_json_warp(string: str) -> dict:
        # 使用正则表达式提取 ```json 与 ``` 之间的部分
        match = re.search(r'```json\s*(.*?)\s*```', string, re.DOTALL)
        if match:
            return try_load_json(match.group(1))
        return {}

    def try_char_warp(string: str) -> dict:
        # 找到JSON部分
        json_start_index = string.find('{')
        json_end_index = string.rfind('}') + 1
        if json_start_index == -1 or json_end_index == 0:
            return {}
        return try_load_json(string[json_start_index:json_end_index])

    # 尝试正则表达式提取，如果失败则尝试字符提取
    return try_json_warp(content) or try_char_warp(content)
