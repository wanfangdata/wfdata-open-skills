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

# 向量搜索可用的 collections
VECTOR_COLLECTIONS = {
    "periodical": "OpenPeriodicalFulltext",
    "thesis": "OpenThesisFulltext",
    "conference": "OpenConferenceFulltext",
    "patent": "OpenPatentFulltext",
    "claw": "OpenClawFulltext",
    "standard": "OpenStandardFulltext",
    "chronicle": "OpenLocalchronicleFulltext",
}


async def wf_data_vector_search(
        query_text: str,
        collections: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    万方数据向量语义搜索

    基于语义相似度的文献检索，适合查找语义相关的文献。

    Args:
        query_text: 自然语言查询文本，如 "自然语言处理在医疗领域的应用"
        collections: 文献类型列表，可选值见 VECTOR_COLLECTIONS，默认为 ["OpenPeriodicalFulltext"]

    Returns:
        语义相关的文献列表

    Example:
        result = await wfdata_vector_search(
            query_text="深度学习在图像识别中的应用",
            collections=["OpenPeriodicalFulltext", "OpenThesisFulltext"]
        )
    """
    # 处理 collections 参数
    if collections is None:
        collections = ["OpenPeriodicalFulltext"]

    # 转换简称为完整名称
    resolved_collections = []
    for col in collections:
        if col in VECTOR_COLLECTIONS:
            resolved_collections.append(VECTOR_COLLECTIONS[col])
        elif col in VECTOR_COLLECTIONS.values():
            resolved_collections.append(col)
        else:
            resolved_collections.append(col)  # 保持原样

    url = f"{WFDATA_BASE_URL}/vectorsearch/query"

    payload = {
        "collections": resolved_collections,
        "vectorParameter": {
            "vector_field": "SentenceVec",
            "vector_value": query_text
        }
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
                        "message": "向量搜索完成"
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

    parser = argparse.ArgumentParser(description='万方数据向量语义搜索')
    parser.add_argument('query_text', help='自然语言查询文本')
    parser.add_argument('--collections', default=["OpenPeriodicalFulltext"], help='文献类型列表，可选值见 VECTOR_COLLECTIONS')

    args = parser.parse_args()
    result = await wf_data_vector_search(query_text=args.query_text,collections=args.collections)
    print(result)
    return result

if __name__ == '__main__':
    asyncio.run(main())