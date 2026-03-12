import asyncio
import os
from typing import List, Optional, Dict, Any

import aiohttp
import requests


# API 配置
WFDATA_BASE_URL = "https://api.wanfangdata.com.cn"

# 从环境变量获取认证信息
WFDATA_APP_KEY = os.environ.get("WFDATA_APP_KEY", "")
WFDATA_APP_CODE = os.environ.get("WFDATA_APP_CODE", "")


def get_headers() -> Dict[str, str]:
    """获取请求头"""
    return {
        "X-Ca-AppKey": WFDATA_APP_KEY,
        "Authorization": f"APPCODE {WFDATA_APP_CODE}",
        "Content-Type": "application/json"
    }


# 可用的 collections 映射
COLLECTIONS = {
    "periodical": "OpenPeriodical",           # 期刊论文（全部）
    "periodical_chi": "OpenPeriodicalChi",    # 中文期刊论文
    "periodical_eng": "OpenPeriodicalEng",    # 英文期刊论文
    "thesis": "OpenThesis",                   # 学位论文
    "conference": "OpenConference",           # 会议论文
    "patent": "OpenPatent",                   # 专利
    "claw": "OpenClaw",                       # 法规
    "cstad": "OpenCstad",                     # 成果
    "standard": "OpenStandard",               # 标准
    "magazine": "OpenMagazine",               # 刊名
    "meeting": "OpenMeeting",                 # 会议名录
    "nstr": "OpenNstr",                       # 科技报告
    "video": "OpenVideo",                     # 视频
    "chronicle": "OpenFZLocalChronicle",      # 方志
    "chronicle_item": "OpenFZLocalChronicleItem",  # 方志条目
}

# def wf_data_query(
#         query: str,
#         collections: Optional[list[str]] = None,
#         rows: int = 10,
#         start: int = 0,
#         sort_name: str = "OfflineScore"):
#     """
#     万方数据文献检索
#
#     Args:
#         query: 搜索关键词，多个关键词用逗号分隔，如 "人工智能,深度学习"
#         collections: 文献类型列表，可选值见 COLLECTIONS，默认为 ["OpenPeriodical"]
#         rows: 返回结果数量，默认 10
#         start: 起始位置，默认 0
#         sort_name: 排序字段，默认 "OfflineScore"
#
#     Returns:
#         搜索结果，包含文献列表
#
#     """
#     if collections is None:
#         collections = ["OpenPeriodical"]
#         # 转换简称为完整名称
#     resolved_collections = []
#     for col in collections:
#         if col in COLLECTIONS:
#             resolved_collections.append(COLLECTIONS[col])
#         elif col in COLLECTIONS.values():
#             resolved_collections.append(col)
#         else:
#             resolved_collections.append(col)  # 保持原样，让 API 报错
#
#     url = f"{WFDATA_BASE_URL}/openwanfang/getQuery"
#
#     payload = {
#         "collections": resolved_collections,
#         "query": query,
#         "sort": {"sort_name": sort_name},
#         "rows": rows,
#         "start": start
#     }
#
#     try:
#         response = requests.post(
#             url,
#             headers=get_headers(),
#             json=payload,
#             timeout=30
#         )
#
#         if response.status_code == 200:
#             result = response.json()
#             return {
#                 "success": True,
#                 "status": response.status_code,
#                 "total": result.get('numFound', 0),
#                 "data": result,
#                 "message": f"搜索到 {result.get('numFound', 0)} 条结果"
#             }
#         else:
#             return {
#                 "success": False,
#                 "status": response.status_code,
#                 "message": f"请求失败，状态码: {response.status_code}",
#                 "response_text": response.text[:200] if response.text else ""
#             }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "message": "请求万方数据API失败"
#         }


async def wf_data_query(
        query: str,
        collections: Optional[List[str]] = None,
        rows: int = 10,
        start: int = 0,
        sort_name: str = "OfflineScore"
) -> Dict[str, Any]:
    """
    万方数据文献检索

    Args:
        query: 搜索关键词，多个关键词用逗号分隔，如 "人工智能,深度学习"
        collections: 文献类型列表，可选值见 COLLECTIONS，默认为 ["OpenPeriodical"]
        rows: 返回结果数量，默认 10
        start: 起始位置，默认 0
        sort_name: 排序字段，默认 "OfflineScore"

    Returns:
        搜索结果，包含文献列表

    Example:
        result = await wfdata_query(
            query="人工智能,机器学习",
            collections=["OpenPeriodical", "OpenThesis"],
            rows=20
        )
    """
    # 处理 collections 参数
    if collections is None:
        collections = ["OpenPeriodical"]

    # 转换简称为完整名称
    resolved_collections = []
    for col in collections:
        if col in COLLECTIONS:
            resolved_collections.append(COLLECTIONS[col])
        elif col in COLLECTIONS.values():
            resolved_collections.append(col)
        else:
            resolved_collections.append(col)  # 保持原样，让 API 报错

    url = f"{WFDATA_BASE_URL}/openwanfang/getQuery"

    payload = {
        "collections": resolved_collections,
        "query": query,
        "sort": {"sort_name": sort_name},
        "rows": rows,
        "start": start
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    headers=get_headers(),
                    json=payload
            ) as response:
                result = await response.json()

                if response.status == 200:
                    return {
                        "success": True,
                        "data": result,
                        "message": f"搜索到 {result.get('numFound', 0)} 条结果"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("message", "请求失败"),
                        "status_code": response.status
                    }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "请求万方数据API失败"
        }


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='万方数据基于关键词的文献检索')
    parser.add_argument('query', help='输入文本')
    parser.add_argument('--collections', default=["OpenPeriodical"], help='文献类型列表，可选值见 COLLECTIONS')
    parser.add_argument('--rows', default=10, help='返回结果数量')
    parser.add_argument('--start', default=0, help='起始位置')
    parser.add_argument('--sort_name', default='OfflineScore', help='排序字段')

    args = parser.parse_args()
    result = await wf_data_query(query=args.query,collections=args.collections, rows=args.rows, start=args.start, sort_name=args.sort_name)
    print(result)
    return result

if __name__ == '__main__':
    asyncio.run(main())