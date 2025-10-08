#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量截断异常文件名前缀（如 format,webp-1759928107939-7.webpg）
usage: 直接 python rename_clean.py
"""
import os
import re
from pathlib import Path

# 需要处理的扩展名
EXTS = ('.webpg', '.png', '.jpg', '.jpeg', '.webp')

# 异常前缀的正则，这里把“format,webp-数字串-数字.扩展名”整段匹配
BAD_PREFIX_RE = re.compile(r'^format,webp-\d+-\d+', re.I)

def clean_name(fname: str) -> str | None:
    """
    如果命中规则，返回干净的新名字；否则返回 None
    """
    p = Path(fname)
    if p.suffix.lower() not in EXTS:
        return None
    new_stem = BAD_PREFIX_RE.sub('', p.stem)
    # 如果清理完和原来一样，说明不需要动
    if new_stem == p.stem:
        return None
    return new_stem + p.suffix

def main(dry_run: bool = True):
    root = Path('.').resolve()
    for dirpath, _, files in os.walk(root):
        for old in files:
            new = clean_name(old)
            if new is None:
                continue
            old_path = Path(dirpath) / old
            new_path = Path(dirpath) / new
            if new_path.exists():
                print(f'[!] 目标已存在，跳过：{old_path}')
                continue
            if dry_run:
                print(f'[预览] {old}  ->  {new}')
            else:
                old_path.rename(new_path)
                print(f'[重命名] {old}  ->  {new}')

if __name__ == '__main__':
    #main(dry_run=True)   # 先预览
    # 确认无误后把上一行改成 main(dry_run=False) 再跑一次
    main(dry_run=False)