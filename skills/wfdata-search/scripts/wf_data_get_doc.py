import asyncio
import os
from typing import List, Optional, Dict, Any

import aiohttp
import requests


# API 配置
WFDATA_BASE_URL = "http://api.wfdata.com"

# 从环境变量获取认证信息
WFDATA_APP_KEY = os.environ.get("WFDATA_APP_KEY", "")



def get_headers() -> Dict[str, str]:
    """获取请求头"""
    return {
        "X-App-Key": WFDATA_APP_KEY,
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


async def wf_data_get_doc(
        collection: str,
        doc_id: str
) -> Dict[str, Any]:
    """
    获取万方文献详情

    Args:
        collection: 文献类型，如 "OpenPeriodical"
        doc_id: 文献ID，如 "dbch202004054"

    Returns:
        文献详情信息

    Example:
        result = await wfdata_get_doc(
            collection="OpenPeriodical",
            doc_id="dbch202004054"
        )
    """
    # 转换简称为完整名称
    if collection in COLLECTIONS:
        collection = COLLECTIONS[collection]

    url = f"{WFDATA_BASE_URL}/openwanfang/getDoc"

    payload = {
        "collection": collection,
        "id": doc_id
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
                        "message": "获取文献详情成功"
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

    parser = argparse.ArgumentParser(description='获取万方文献详情')
    parser.add_argument('doc_id', help='文献ID')
    parser.add_argument('--collection', default="OpenPeriodical", help='文献类型列表，可选值见 COLLECTIONS')


    args = parser.parse_args()
    result = await wf_data_get_doc(doc_id=args.doc_id,collection=args.collection)
    print(result)
    return result

if __name__ == '__main__':
    asyncio.run(main())
