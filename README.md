# wfdata-search

万方数据文献检索技能（Skill）

`wfdata-search` 是一个用于访问 **万方数据开放文献检索平台** 的技能，提供统一的 API 调用能力，支持：

* 文献关键词检索
* 文献详情获取
* 基于语义的全文向量搜索

该技能适用于 **AI Agent、科研助手、知识检索系统等场景**，可以帮助用户快速查找相关学术资源。

---

# 功能特性

本技能提供三种核心能力：

| 功能     | 说明               |
| ------ | ---------------- |
| 文献检索   | 通过关键词搜索万方数据库中的文献 |
| 文献详情获取 | 根据文献 ID 获取完整文献信息 |
| 语义搜索   | 使用自然语言查询语义相关的论文  |

---

# 工具列表

本技能提供以下三个工具：

| 工具名称                   | 功能      |
| ---------------------- | ------- |
| `wfdata_query`         | 文献关键词检索 |
| `wfdata_get_doc`       | 获取文献详情  |
| `wfdata_vector_search` | 向量语义搜索  |

---

# 典型使用流程

AI Agent 在执行科研任务时通常使用以下流程：

```
用户问题
   ↓
wfdata_vector_search（语义检索）
   ↓
获取相关论文 ID
   ↓
wfdata_get_doc（获取论文详情）
   ↓
整理科研信息
```

如果用户使用关键词检索：

```
用户关键词
   ↓
wfdata_query
   ↓
获取文献ID
   ↓
wfdata_get_doc
```

---

# 文献资源类型

系统支持检索以下文献资源：

| 类型   | collection           |
| ---- | -------------------- |
| 期刊论文 | OpenPeriodical       |
| 中文期刊 | OpenPeriodicalChi    |
| 英文期刊 | OpenPeriodicalEng    |
| 学位论文 | OpenThesis           |
| 会议论文 | OpenConference       |
| 专利   | OpenPatent           |
| 法规   | OpenClaw             |
| 成果   | OpenCstad            |
| 标准   | OpenStandard         |
| 科技报告 | OpenNstr             |
| 刊名   | OpenMagazine         |
| 会议名录 | OpenMeeting          |
| 视频   | OpenVideo            |
| 方志   | OpenFZLocalChronicle |

---

# 全文语义检索资源

支持以下全文资源库：

| 类型   | collection                 |
| ---- | -------------------------- |
| 期刊全文 | OpenPeriodicalFulltext     |
| 学位全文 | OpenThesisFulltext         |
| 会议全文 | OpenConferenceFulltext     |
| 专利全文 | OpenPatentFulltext         |
| 法规全文 | OpenClawFulltext           |
| 标准全文 | OpenStandardFulltext       |
| 方志全文 | OpenLocalchronicleFulltext |

---

# API 文档

完整 API 文档请参考：

```
reference/api-catalog.md
```

该文档包含：

* API 地址
* 请求参数
* 返回数据结构
* 文献字段说明
* 向量搜索参数

---

# Skill 配置

Skill 的核心定义文件为：

```
SKILLS.md
```

其中定义了：

* Skill 名称
* Skill 描述
* 可用工具
* 调用示例
* 推荐调用流程

---

# 认证方式

所有接口请求需要以下 Header：

| Header        | 说明               |
| ------------- | ---------------- |
| X-Ca-AppKey   | 应用 Key           |
| Authorization | APPCODE          |
| Content-Type  | application/json |

---

# 示例

关键词检索：

```
query = "人工智能,深度学习"

result = await wfdata_query(
    query=query,
    collections=["OpenPeriodical","OpenThesis"],
    rows=20
)
```

语义检索：

```
result = await wfdata_vector_search(
    query_text="自然语言处理在医疗领域的应用"
)
```

获取文献详情：

```
result = await wfdata_get_doc(
    collection="OpenPeriodical",
    doc_id="dbch202004054"
)
```

---

# 适用场景

该 Skill 适用于：

* AI 科研助手
* 文献推荐系统
* 学术搜索引擎
* 智能问答系统
* RAG 知识检索

---

# 目录结构

```
wfdata-search
├── README.md
├── SKILLS.md
└── reference
    └── api-catalog.md
```

---

# License

Copyright © 万方数据
