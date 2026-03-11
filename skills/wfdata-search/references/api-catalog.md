# 开放文献检索平台 API Reference

**Base URL**：`https://api.wanfangdata.com.cn`
**请求方式**：`POST`
**Content-Type**：`application/json`

本平台提供三类核心接口：

1. **Query 检索接口**：通过 SOLR 查询语句检索文献
2. **Vector Search 向量检索接口**：通过自然语言句子进行全文片段检索
3. **Get 详情接口**：根据文献 ID 获取单条文献详情

---

# 目录

* [检索接口](#检索接口)

  * [1. Query 文献检索](#1-query-文献检索)
  * [2. Vector 全文句子检索](#2-vector-全文句子检索)
* [文献接口](#文献接口)

  * [3. Get 文献详情](#3-get-文献详情)
* [附录](#附录)

  * [资源类型](#资源类型)

---

# 检索接口

---

# 1. Query 文献检索

* **URL**：`/openwanfang/getQuery`
* **Method**：`POST`
* **描述**：通过 PQ 查询表达式检索文献记录，支持过滤、排序、分页等功能。

---

## 请求参数

| 参数              | 类型          | 必填 | 说明                                       |
| --------------- | ----------- | -- | ---------------------------------------- |
| collections     | []string    | 是  | 检索资源库（Solr collection 或别名）               |
| query           | string      | 是  | PQ 查询表达式，例如 `标题:人工智能 AND 年份:[2020 TO *]` |
| filters         | []Filter    | 否  | 用于对检索结果进行字段过滤 ，相当于 **Solr 的 fq 条件**  |
| returned_fields | []string    | 否  | 返回字段列表                                   |
| sort            | SortRequest | 否  | 用于指定检索结果的排序方式                     |
| start           | int         | 否  | 起始位置，默认 0                                |
| rows            | int         | 否  | 返回数量，默认 20                               |

## Filter 参数说明

| 参数    | 类型       | 必填 | 说明                                      |
| ----- | -------- | -- | --------------------------------------- |
| field | string   | 是  | 过滤字段，例如 `DBID`、`文献类型`                   |
| value | string   | 是  | 过滤值，可以使用 mapping 值或逻辑表达式                |
| tags  | []string | 否  | 为 filter 添加 tag，用于 function query 或高级检索 |

## Sort 参数说明

| 参数    | 类型     | 必填 | 说明                            |
| ----- | ------ | -- | ----------------------------- |
| by    | string | 否  | 排序字段，可以是字段名称或 PQ 字段别名         |
| order | string | 否  | 排序方式：`ASC` 或 `DESC`，默认 `DESC` |

---

## SortRequest

| 参数           | 类型       | 必填 | 说明                          |
| ------------ | -------- | -- | --------------------------- |
| sorts        | Sort[]   | 否  | Solr sort 排序字段              |
| boost_querys | []string | 否  | 使用函数干预 score 排序（Solr bf 参数） |
| sort_name    | string   | 否  | 使用系统预置排序                    |
| normalize    | bool     | 否  | 是否对 score 进行归一化             |

---

## 请求示例

### 示例 1：默认排序

```json
{
  "collections": ["OpenPeriodical"],
  "query": "(人工智能 AND 医学) AND PublishYear:[2020 TO *]",
  "returned_fields": ["Title", "Id", "PublishYear"],
  "sort": {
    "sort_name": "OfflineScore"
  }
}
```

---

### 示例 2：按照相关度和年份排序

```json
{
  "collections": ["OpenPeriodical"],
  "query": "(人工智能 AND 医学影像)",
  "returned_fields": ["Title", "Id", "PublishYear"],
  "sort": {
    "sorts": [
      {
        "by": "score",
        "order": "DESC"
      },
      {
        "by": "PublishYear",
        "order": "DESC"
      }
    ]
  }
}
```

### 示例 3：多个论文类型过滤

```json
{
  "collections": ["OpenPeriodical"],
  "query": "(人工智能 AND 医学影像)",
  "returned_fields": ["Title", "Id", "PublishYear"],
  "sort": {
    "sorts": [
      {
        "by": "score",
        "order": "DESC"
      },
      {
        "by": "PublishYear",
        "order": "DESC"
      }
    ]
  },
  "filters":[
    {
      "field":"Type",
      "value":"(Periodical OR Thesis)"
    }
  ]
}
```

---

## 返回字段

| 字段               | 说明      |
| ---------------- | ------- |
| documents        | Document        | 返回的文献列表 |
| num_found        | int32 |               命中文献数量  |

## Document 论文的元数据

| Field         | Type                                     | Label    | Description                              |
| ------------- | ---------------------------------------- | -------- | ---------------------------------------- |
| resource_type | [string](#string)                        |          | 资源类型比如 Periodical,Thesis,Conference 等等   |
| fields        | [Document.FieldsEntry](#Document.FieldsEntry) | repeated | 所有字段都写入当前字段 |

# 2. Vector 全文句子检索

* **URL**：`/vectorsearch/query`
* **Method**：`POST`
* **描述**：通过自然语言句子进行全文片段检索，系统会基于向量索引进行相似度匹配。

该接口适用于：

* 自然语言搜索
* 语义检索
* 问题式检索

---

## 请求参数

| 参数              | 类型              | 必填 | 说明     |
| --------------- | --------------- | -- | ------ |
| collections     | []string        | 是  | 全文资源库  |
| vectorParameter | VectorParameter | 是  | 向量检索参数 |
| returned_fields | []string        | 否  | 返回字段   |

---

## VectorParameter 参数说明

| 参数           | 类型     | 必填 | 说明                        |
| ------------ | ------ | -- | ------------------------- |
| vector_field | string | 是  | 向量字段，全文检索使用 `SentenceVec` |
| vector_value | string | 是  | 自然语言查询句子                  |
| v_distance   | float  | 否  | 欧氏距离阈值                    |
| v_nprobe     | int    | 否  | 搜索簇数量                     |
| top_n        | int    | 否  | 每个 segment 返回条数           |

---

## 请求示例

```json
{
  "collections": ["OpenPeriodicalFulltext"],
  "vectorParameter": {
    "vector_field": "SentenceVec",
    "vector_value": "人工智能在医学影像诊断中的应用"
  },
  "returned_fields": ["Title", "Id", "Abstract"]
}
```

---

## 返回字段

| 字段               | 说明      |
| ---------------- | ------- |
| documents        | Document        | 返回的文献列表 |
| num_found        | int32 |               命中文献数量  |

## Document 论文的元数据

| Field         | Type                                     | Label    | Description                              |
| ------------- | ---------------------------------------- | -------- | ---------------------------------------- |
| resource_type | [string](#string)                        |          | 资源类型比如 Periodical,Thesis,Conference 等等   |
| fields        | [Document.FieldsEntry](#Document.FieldsEntry) | repeated | 所有字段都写入当前字段 |

## FieldsEntry 字段
| Field         | Type                                     | Label    | Description                              |
| ------------- | ---------------------------------------- | -------- | ---------------------------------------- |
| Id | [string](#string)                        |          | 句子ID，组成方式是论文ID^段落偏移^当前句子在段落中的偏移   |
| ParagraphLength | int32 |  | 段落长度 |
| SentenceLength | int32 |  | 句子长度 |
| Type | [string](#string) |  | 资源类型例如Periodical,Thesis,Conference 等等 |
| Centroid | int32 |  | 句子所在的句子簇的编号 |
| __paragraph__ | [string](#string) |  | 当前句子在论文中的段落 |
| __sentence__ | [string](#string) |  | 当前句子 |
| __sentence__ | int32 |  | 句子在段落中的偏移 |

---

# 文献接口

---

# 3. Get 文献详情

* **URL**：`/openwanfang/getDoc`
* **Method**：`POST`
* **描述**：根据文献 ID 获取文献详细信息。

---

## 请求参数

| 参数              | 类型       | 必填 | 说明     |
| --------------- | -------- | -- | ------ |
| collection      | string   | 是  | 文献资源库  |
| id              | string   | 是  | 文献 ID  |
| returned_fields | []string | 否  | 指定返回字段 |

---

## 请求示例

```json
{
  "collection": "OpenPeriodical",
  "id": "dbch202004054"
}
```

---

## 返回字段

| 字段            | 说明    |
| ------------- | ----- |
| resource_type | 资源类型  |
| fields        | 文献字段  |
| id            | 文献 ID |

---

# 附录

---

# 资源类型

| 资源库            | 类型   |
| -------------- | ---- |
| OpenPeriodical | 期刊论文 |
| OpenPeriodicalChi | 中文期刊论文 |
| OpenPeriodicalEng | 英文期刊论文 |
| OpenThesis     | 学位论文 |
| OpenConference | 会议论文 |
| OpenPatent     | 专利   |
| OpenStandard   | 标准   |
| OpenClaw       | 法规   |
| OpenCstad      | 科研成果 |
| OpenMagazine      | 刊名 |
| OpenMeeting      | 会议名录 |
| OpenNstr      | 科技报告 |
| OpenFZLocalChronicle      | 地方志 |
| OpenFZLocalChronicleItem      | 地方志条目 |
| OpenVideo      | 视频 |

---

# 全文资源

| 资源库                    | 类型     |
| ---------------------- | ------ |
| OpenPeriodicalFulltext | 期刊全文   |
| OpenThesisFulltext     | 学位全文 |
| OpenConferenceFulltext | 会议全文   |
| OpenPatentFulltext     | 专利全文   |
| OpenStandardFulltext   | 标准全文   |
| OpenClawFulltext       | 法规全文   |
| OpenStandardFulltext   | 标准全文   |
| OpenLocalchronicleFulltext   | 标准全文   |


# 资源类型

### Book

| Field             | Type              | Label    | Description                              |
| ----------------- | ----------------- | -------- | ---------------------------------------- |
| Id                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 题名, 标题, t, name, 名称, 书 说明: 书名 |
| Subtitle          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 副题名 说明: 副标题 |
| Creator           | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者 |
| CreatorForSearch  | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, a, creaters, author, authors, 人, 作者, 著者 说明: 该字段为 CopyField,源于 Creator |
| Publisher         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 出版社 说明: 出版单位 |
| PublisherLocation | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 出版单位地区 |
| ISBN              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: ISBN |
| PublishDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 出版日期 |
| PublishYear       | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: Date, date 说明: 出版年 |
| PageNum           | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| ThirdpartyUrl     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 第三方链接 |
| Type              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| SingleSourceDB    | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 单值来源数据库 |
| ContentSearch     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索（缺省字段检索） |
| CitedCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| CitedScore        | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore     | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore         | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore         | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |

### Claw

| Field              | Type              | Label    | Description                              |
| ------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: general |
| Type               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| Title              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, title, 篇名, 主题, 题名或关键词 说明: 规名称 |
| IssueUnit          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 作者单位, organization, issuedepartment, iu, 颁布部门 说明: 颁布部门 |
| IssueNumber        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 发文号, in, 发文文号 说明: 发文文号 |
| ContentClassCode   | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 内容分类码 |
| ContentClassName   | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 内容分类名称 |
| TradeClassCode     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 行业分类码 |
| TradeClassName     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 行业分类名称 |
| FinalCourt         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 终审法院 说明: 终审法院 |
| ContentSearch      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索 |
| SingleSourceDB     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 来源数据库 |
| EffectLevel        | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 效力级别 说明: 效力级别 |
| EffectCode         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 效力代码 |
| Effect             | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 时效性 说明: 时效性 |
| ApprovalDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 批准日期 |
| SignDate           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 签字日期 |
| IssueDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 颁布日期, 日期, 颁布时间, 出版时间 说明: 颁布日期 |
| PublishDate        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布时间 |
| PublishYear        | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: date, Date 说明: 发布年 |
| ApplyDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 实施日期 |
| ExpiryDate         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 失效日期 |
| FinalDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 终审日期 |
| MediateDate        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 调解日期 |
| URLPath            | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: URL 全文 |
| PDFPath            | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: PDF 全文 |
| HasFulltext        | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文 |
| DBID               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 内容分类 说明: 库别代码 |
| MetadataViewCount  | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| DownloadCount      | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| MetadataOnlineDate | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘上网日期 |
| ExportCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| CitedCount         | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| CitedScore         | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore      | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore          | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| Language           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 语种 |
| Creator            | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 用于跨库检索聚类使用，作者 |
| OrganizationNorm   | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 用于跨库检索聚类使用，规范机构名 |
| AttachmentTitle    | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 附件题名 |
| AttachmentDir      | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 附件路径 |
| FulltextScore      | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore          | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### Conference

| Field                    | Type              | Label    | Description                              |
| ------------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title                    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, titles, 题, 题目, 篇名 说明: 第一位置为中文题名，第二位为英文题名，往后顺延为其他语种题名，如果没有中文，则第一位置为英文题目 |
| Creator                  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者,中文作者及其对应拼音作者顺序一致，只有中文或只有英文作者没有该映射关系 |
| FirstCreator             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 第一作者 说明: 第一作者 |
| ScholarId                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 学者 Id,该字段与作者字段（Creator）映射，即使没有值，也用空值(&#34;&#34;)占位 |
| CreatorForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, a, creaters, author, authors, 人, 作者, 著者 说明: 作者检索字段(只用于检索) |
| OrganizationNorm         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 规范机构名 |
| OrganizationNew          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 最新机构名,当前和规范机构名值一致，今后可能会整理最新机构名 |
| OriginalOrganization     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 原机构名(作者发文时的机构名)，详情页展示用，目前主站要求展示非对应（与作者）的机构名称 |
| OrganizationForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 作者单位, 机构, org, 单位, 机构名称, Organization 说明: 机构检索字段(只用于检索) |
| ClassCode                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 原文分类号（聚类，显示），会议论文都是人工标引的分类号，存放在[class_code]字段 |
| MachinedClassCode        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 存放[auto_classcode]，机标分类号 |
| ClassCodeForSearch       | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: false, 多值: true 别名: 分类号, clc, 分, 分类, c, 中图分类号 说明: 原文分类号检索字段.该字段为 copyfield 字段,由 ClassCode，MachinedClassCode 组成，使用指定的映射表，做索引 |
| ContentSearch            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索.该字段为 copyfield 字段,源于 Title，KeywordForsearch(由于该字段为 Copy 字段，所以需要写全部源字段)，Abstract，PeriodicalTitle，Fund |
| Keywords                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词,会议论文都是人工标引的关键词，存放在[keywords]、[trans_keys]字段；[orig_keys]全部空值； |
| ForeignKeywords          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文关键词,会议论文都是人工标引的关键词，存放在[keywords]、[trans_keys]字段；[orig_keys]全部空值； |
| MachinedKeywords         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 机标关键词,会议论文都是人工标引的关键词，存放在[keywords]、[trans_keys]字段；[orig_keys]全部空值； |
| KeywordForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段.该字段为 CopyField，源于 Keywords，ForeignKeywords，MachinedKeywords |
| Abstract                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 第一位置为中文摘要，第二位为外文文摘。如果没有中文，则第一位置为外文摘要 |
| CitedCount               | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| SourceDB                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 来源数据库 如 WF,CNKI,CQVIP 等，共几十个来源。 |
| SingleSourceDB           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 来源数据库 说明: 单值来源数据库 |
| PublishDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 出版时间(原文) |
| MetadataOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文文摘上网日期 |
| FulltextOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文全文上网日期 |
| ServiceMode              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 全文服务模式,0:没版权，1：有版权 |
| HasFulltext              | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文,0：没全文，1：有全文 |
| PublishYear              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: Date, date 说明: 出版年,和出版时间统一，聚类使用，数据源提供了该字段 |
| Page                     | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页码 |
| PageNo                   | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| FulltextPath             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 全文路径 |
| DOI                      | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: DOI |
| AuthorOrg                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 作者机构字段,值为：author1:org1;author2:org2;中英文作者都有，中文作者，优先匹配中文机构，英文作者优先匹配英文机构 |
| ThirdPartyUrl            | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 第三方链接字段,为：db1:url1,id1;db2:url2,id2 |
| Language                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 语种 |
| MeetingId                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 会议标识 说明: 会议 ID |
| MeetingTitle             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 会议名称, conference 说明: 会议名称。第一位置为会议名，第二位位置为拼音会议名(有中文刊名时存在)，第三位置为英文会议名，第四位其他语种会议名(韩文) |
| MeetingTitleForFacet     | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 会议名称（聚类） 说明: 会议名称 |
| MeetingArea              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 举办地 说明: 会议地点 |
| MeetingDate              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 会议时间 |
| MeetingYear              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 会议年份 |
| Sponsor                  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 主办单位, 主办方 说明: 会议主办单位 |
| Publisher                | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 出版单位 |
| PublishArea              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 出版地 |
| MeetingCorpusId          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 会议文集 Id |
| MeetingCorpus            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 会议文集 |
| MeetingLevel             | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 会议级别 |
| MetadataViewCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ThirdpartyLinkClickCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 第三方链接点击次数 |
| DownloadCount            | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| Type                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| CitedScore               | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore                | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| MeetingClassCode         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 会议名录分类号 |
| FulltextScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### Cstad

| Field                 | Type              | Label    | Description                              |
| --------------------- | ----------------- | -------- | ---------------------------------------- |
| Id                    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, titles, 名称, 成果名称 说明: 成果名称 |
| Creator               | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 完成人 |
| CreatorForSearch      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 完成人, 创作者, creaters, author, authors, 作者 说明: 完成人检索字段(只用于检索) |
| Contact               | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 联系人 说明: 联系人 |
| ContactUnit           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 联系单位 说明: 联系单位名称 |
| ContactAddress        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 联系单位地址 |
| Fax                   | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 传真 |
| Postcode              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 邮政编码 |
| Email                 | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 电子邮件 |
| ApplicationAgency     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 申报单位 说明: 申报单位名 |
| ApplicationDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 申报日期 |
| AppraisalAgency       | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 鉴定单位 说明: 鉴定部门 |
| AppraisalDate         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 鉴定日期 |
| AppraisalYear         | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 鉴定年 |
| RecommendDept         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 推荐部门 |
| RecommendDeptCode     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 推荐部门码 |
| RecommendDate         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推荐日期 |
| RecommendNo           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推荐登记号 |
| RegisterDept          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 登记部门 说明: 登记部门 |
| RegisterDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 登记日期 |
| RegisterNo            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 登记号 |
| RegisterDeptCode      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 登记部门码 |
| PlanName              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 计划名称 |
| PlanDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 列入时间 |
| StartEndDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 工作起止时间 |
| Organization          | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 完成单位 |
| OrganizationForSearch | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 作者单位, 机构, org, 单位, 机构名称, 完成单位 说明: 完成单位(只用于检索) |
| ClassCode             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 分类号（聚类，显示） |
| ClassCodeForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: false, 多值: true 别名: 分类号, clc, 分, 分类, c, 中图分类号 说明: 分类号检索字段(只用于检索) |
| ContentSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索 |
| Abstract              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 成果简介 |
| Keywords              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词 |
| KeywordForSearch      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段(只用于检索) |
| PublishYear           | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 说明: 成果公布年份 |
| PublishDate           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 公布年份, 出版时间 说明: 发布时间 |
| Page                  | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页码 |
| PageNo                | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| AchievementType       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 类别 说明: 成果类别 |
| AchievementLevel      | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 成果水平 说明: 成果水平 |
| AchievementLevelSort  | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 成果级别 说明: 成果水平排序 |
| AchievementSecurity   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 成果密级 说明: 成果密级 |
| TradeCode             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 应用行业码 |
| TradeName             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 行业分类 说明: 应用行业名称 |
| PatentCount           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 专利项数 |
| PatentAuthorizationNo | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 专利授权号 |
| PatentApplicationNo   | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 专利申请号 |
| Province              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 省市, 地区 说明: 省市 |
| TransferNote          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让注释 |
| TransferCondition     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让条件 |
| TransferContent       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让内容 |
| TransferRange         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让范围 |
| TransferWay           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让方式 |
| TransferPayment       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 转让费 |
| Investment            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 投资金额 |
| InvestNote            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 投资注释 |
| ConstructionPhase     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 建设期 |
| InvestInstruction     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 投资说明 |
| OutValue              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 产值 |
| Tax                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 利税 |
| ForeignExchange       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 创汇 |
| CostSaved             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 节资 |
| PromoWay              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推广方式 |
| PromoRange            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推广范围 |
| PromoInvestigation    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推广跟踪 |
| PromoEffect           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 推广情况说明 |
| MetadataViewCount     | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ExportCount           | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| CitedCount            | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 被引次数 |
| Limited               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 限制使用 |
| Type                  | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 |
| Award                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 获奖情况 说明: 获奖情况 |
| SingleSourceDB        | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 来源数据库 |
| MetadataOnlineDate    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 文摘上网日期 |
| CitedScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore         | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore             | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore             | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| FulltextScore         | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore             | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### LocalChronicle

| Field               | Type              | Label    | Description                              |
| ------------------- | ----------------- | -------- | ---------------------------------------- |
| Id                  | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: BookID 说明: 志书 ID |
| Title               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: BookTitle, 题名, 志书名 说明: 志书名 |
| Editorial           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 编纂单位 说明: 编纂单位 |
| Editor              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 编纂人员 说明: 编纂人员 |
| Publisher           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 出版单位 说明: 出版单位 |
| ISBN                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: ISBN |
| TimeLimit           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 内容时限 |
| IsNational          | [bool](#bool)     |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 是否全国 |
| Province            | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 省 |
| City                | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 市 |
| County              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 县 |
| RegionCode          | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 行政区代码 |
| RegionCodeForSearch | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 行政区代码检索字段 |
| CategoryLevel       | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 分类级别 |
| RegionLevel         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 地区级别 |
| AlbumCategory       | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 专辑分类 |
| Keywords            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词 |
| Volume              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 卷数 |
| Dynasty             | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 朝代 |
| ReignTitle          | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 年号 |
| ReignYear           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 年代 |
| Edition             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 版本 |
| DBID                | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 新方志：FZ_New；旧方志：FZ_Old |
| OnlineDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 上线时间 |
| Abstract            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 正文, 摘要 说明: 简介 |
| PublishDate         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 出版时间 |
| PublishYear         | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 出版年份 |
| PageNo              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| MetadataViewCount   | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| DownloadCount       | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount         | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| CitedCount          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| Type                | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 资源类型 |
| SingleSourceDB      | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 单值来源数据库 |
| BoughtUserId        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 已购用户 ID |
| YearCode            | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 年代分级 |
| CitedScore          | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore       | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore           | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore           | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| FulltextScore       | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore           | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### LocalChronicleItem

| Field                  | Type              | Label    | Description                              |
| ---------------------- | ----------------- | -------- | ---------------------------------------- |
| Id                     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 条目 ID |
| Title                  | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 题名, 标题 说明: 题名 |
| ParentId               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 上一级条目 ID |
| BookId                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 志书 ID |
| BookTitle              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 志书名 说明: 方志中文名 |
| Keywords               | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词，对应关键字 |
| Content                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 正文 说明: 正文节选 |
| Editorial              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 编纂单位 说明: 编纂单位 |
| Editor                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 编纂人员 说明: 编纂人员 |
| Publisher              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 出版单位 |
| PublishDate            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 出版时间 |
| PublishYear            | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: date, Date 说明: 出版年份 |
| ISBN                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: ISBN |
| TimeLimit              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 内容时限 |
| TimeLimitBegin         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 内容时限开始时间：公元前对应负值 |
| TimeLimitEnd           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 内容时限结束时间 |
| IsNational             | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: boolean 类型，是否全国，0 表示 false，1 代表 true |
| Province               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 省 |
| City                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 市 |
| County                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 县 |
| RegionCode             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 行政区代码 |
| RegionCodeForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 行政区代码 forsearch |
| Page                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 页码 |
| PageNo                 | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| Dynasty                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 朝代 |
| ReignTitle             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 年号 |
| ReignYear              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 年代 |
| VolumeSort             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 旧方志卷排序 |
| Volume                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 旧方志卷 |
| ItemType               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 条目类型 |
| AlbumCategory          | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 专题分类 |
| AlbumCategoryForSearch | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 专题分类检索 |
| RealLevel              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 条目级次 |
| Sheet                  | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 篇名 |
| SheetInfo              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 篇名 ID |
| Chapter                | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 章名 |
| ChapterInfo            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 章名 ID |
| Section                | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 节名 |
| SectionInfo            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 节名 ID |
| Item                   | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 目名 |
| ItemInfo               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 目名 ID |
| SubItem                | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 子目名 |
| SubItemInfo            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 子目名 ID |
| No                     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 序号，章节顺序，对应章节层次代码 |
| ItemLevel              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 条目级别 |
| ItemLevelCode          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 条目级别代码 |
| Location               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 全文位置 |
| BeginPara              | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 起始书签定位 |
| EndPara                | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 结束书签定位 |
| DBID                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: DBID：FZ_New , FZ_Old |
| FilePath               | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 旧方志志书路径，新方志该值为空 |
| StartPage              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 新方志整本阅读（两个 pdf 合并）每条目起始页 |
| OnlineDate             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 出版时间 |
| BoughtUserId           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 已购用户 ID |
| MetadataViewCount      | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| DownloadCount          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount            | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| SingleSourceDB         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 单值来源数据库 |
| Type                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 资源类型 |
| YearCode               | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 年代分级 |
| CitedScore             | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| FulltextScore          | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 除期刊外，其他资源该字段不赋值 |
| CoreScore              | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 除期刊外，其他资源该字段不赋值 |
| YearScore              | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |

### Magazine

| Field               | Type              | Label    | Description                              |
| ------------------- | ----------------- | -------- | ---------------------------------------- |
| Id                  | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 期刊 id |
| Title               | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 刊名(中文刊名、外文刊名) |
| TitleNoTokenizer    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 刊名(中文刊名、外文刊名) |
| Language            | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 语种(中文语种、外文语种) |
| FormerTitle         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 曾用刊名 |
| Address             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 地址 |
| Postcode            | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 邮政编码 |
| Url                 | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 网址 |
| Telephone           | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 电话 |
| Email               | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: e-mail |
| Fax                 | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 传真 |
| ISSN                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 期刊印刷版 ISSN |
| CN                  | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 期刊印刷版 CN |
| LastYear            | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 最新更新刊年份 |
| LastIssue           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 最新更新刊期 |
| YearIssue           | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 刊期 JSON 格式 年份倒序,期号正序排列 ,格式 year:1,2,3 |
| Introduction        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 简介, introduction, abstract 说明: 期刊简介 |
| ClassCode           | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 期刊分类, 分类, category, class, 学科分类 说明: 学科 |
| Editorial           | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 别名: 编辑单位, newsroom 说明: 编辑部名称 |
| Award               | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 获奖情况 |
| PrimeColumn         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 主要栏目 |
| Sponsor             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 主办单位, sponsor, 主办机构 说明: 主办单位名称 |
| SponsorRegion       | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 地区, region, province, 省, 省市 说明: 主办单位地域 |
| CompetentDepartment | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 主管部门名称 |
| Director            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 主任 |
| Chief               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 总编 |
| ChiefEditor         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 主编 |
| CorePeriodical      | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 核心 说明: 取值为：PKU,ISTIC,CA,EI,CBST,AJ,SA 等 |
| ImpactFactor        | [double](#double) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 影响因子 说明: 影响因子 |
| ArticleNo           | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 文献量 说明: 期刊载文量 |
| DownloadCount       | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 下载量 说明: 下载次数 |
| CitedCount          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 被引频次 说明: 被引次数 |
| ArticleAvgDownload  | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 篇均下载 |
| Initial             | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 刊名拼音首字母 |
| IssuedPeriod        | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 出版周期 |
| FoundYear           | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 创刊年份 |
| IsStopped           | [bool](#bool)     |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: true 停刊 false 未停刊 |
| IsPrePublished      | [bool](#bool)     |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 是否有优先出版论文 |
| FundArticleCount    | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 基金文献量 |
| CorePeriodicalYear  | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 核心刊收录年，取值说明：核心刊标志:year1,year2,…&#34;例如：ISTIC:2019,2018,2017。 |
| ContentSearch       | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 说明: 多字段内容检索 |
| Type                | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |

### Meeting

| Field         | Type              | Label    | Description                              |
| ------------- | ----------------- | -------- | ---------------------------------------- |
| Id            | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 会议 id |
| Title         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: TITLE, 会议名称, 名称 说明: 会议名(中文名、外文名) |
| Initial       | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 拼音首字母 |
| Sponsor       | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 主办单位 说明: 会议主办单位名称/会议论文主办单位 |
| SponsorType   | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 单位类型 |
| NO            | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 届次 |
| Level         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 会议级别 |
| Venue         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 地点 说明: 会议地点 |
| ClassCode     | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 分类号, clc, 分, 分类, c, 中图分类号, 学科分类 说明: 学科 |
| Series        | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 系列会议 |
| Date          | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 时间 说明: 会议日期 |
| Year          | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 年份 说明: 会议年份 |
| CitedCount    | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 被引频次 说明: 被引数量 |
| DownloadCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 下载量 说明: 下载次数 |
| ArticleNO     | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 文献量 说明: 论文数 |
| ContentSearch | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 说明: 检索字段 |
| Type          | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |

### Nstr

| Field                    | Type              | Label    | Description                              |
| ------------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title                    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, name, 名称, 报告名称 说明: 科技报告名称 |
| Initial                  | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 报告名称(拼音)首字母 |
| Creator                  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者,中文作者及其对应拼音作者顺序一致，只有中文或只有英文作者没有该映射关系 |
| CreatorForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, a, creaters, author, authors, 人, 作者, 著者 说明: 该字段为 CopyField,源于 Creator |
| Organization             | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者单位 |
| OrganizationForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 作者单位, 机构, org, 单位, 机构名称 说明: 作者单位(只用于检索)该字段为 copyfield 字段，源于 Organization |
| ClassCode                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 中图分类号 说明: 分类号（聚类，显示） |
| Keywords                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词 |
| ForeignKeywords          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文关键词 |
| KeywordForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段(只用于检索) |
| Abstract                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 摘要 |
| PlanName                 | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 计划名称 说明: 计划名称 |
| PlanNameForSearch        | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 计划名称，检索 |
| ProjectName              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 项目名称 说明: 项目名称 |
| ProjectNum               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 项目编号 |
| ContentSearch            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索（缺省字段检索） |
| SourceDB                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 来源数据库 |
| IssueDate                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布时间 |
| PublishDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 发布时间 |
| PublishYear              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 日期, date, Date 说明: 发布年 |
| ReportType               | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 报告类型 |
| ReportRange              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 报告范围 |
| OpenRange                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 公开范围 |
| ApprovalDate             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 立项批准时间 |
| Administrators           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 主管部门 |
| TechnicalField           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 相关技术领域 |
| PageNum                  | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| LibNum                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 馆藏号 |
| Language                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 语种 |
| PreparationTime          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 编制时间 说明: 编制时间 |
| DBID                     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 用以区分中外文报告，中文：CHI,外文：ENG |
| MetadataViewCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ThirdpartyLinkClickCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 第三方链接点击次数 |
| ExportCount              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| CitedCount               | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| Type                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| SingleSourceDB           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 单值来源数据库 |
| Area                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 地域 |
| Subject                  | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 规范学科分类名称 |
| CitedScore               | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore                | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| FulltextScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### Patent

| Field                    | Type              | Label    | Description                              |
| ------------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title                    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, name, title, 专利名称, 名称, 题名或关键词 说明: 专利名称(第一位置为中文题名，第二位为英文题名，往后顺延为其他语种题名，如果没有中文，则第一位置为英文题目) |
| PatentCode               | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 申请号, 申请、专利号, 申请/专利号, 申请号/专利号 说明: 申请号，申请、专利号 |
| PublicationNo            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 公开/公告号, 公开号/公告号 说明: 公告/公开号 |
| Inventor                 | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 发明人 |
| InventorForSearch        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, author, inventor, 设计人, 发明人, 发明人/设计人, 发明/设计人, 作者 说明: 发明人检索字段(只用于检索) 该字段为 CopyField,源于 Inventor |
| Applicant                | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 申请人 |
| ApplicantForSearch       | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 申请人, applicant, 专利权人, 申请人/专利权人, 作者单位, 申请（专利权）人 说明: 申请人检索字段(只用于检索) 该字段为 CopyField,源于 Applicant；由于该字段人名公司名都存在，所以未使用作者索引（text_author）。 |
| MainClassCode            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 主分类号 说明: 主分类号 |
| MainClassCodeForSearch   | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 主分类号(用于检索) |
| IPCClassCode             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 分类号 |
| IPCClassCodeForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 分类号 说明: 分类号(用于检索) |
| ContentSearch            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索 该字段为 CopyField，源于 Title，Abstract |
| Abstract                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 摘要(第一位置为中文摘要，第二位为外文文摘。如果没有中文，则第一位置为外文摘要) |
| PatentType               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 专利类型 |
| SingleSourceDB           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 来源数据库 |
| ApplicationDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 申请日, applicationdate, 申请时间 说明: 申请日 |
| PublicationDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 日期, 公开日, 公告日期, publicationdate, 公开时间 说明: 公开/公告日 |
| CountryOrganization      | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 国家/组织（代码） |
| ApplicantArea            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 申请/专利权人所在地区(该字段的值有:国家,省市) |
| ApplicantAddress         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 申请/专利权人地址 |
| Agency                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 代理机构 说明: 代理机构名称 |
| Agent                    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 代理人 说明: 代理人 |
| SignoryItem              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 主权项 说明: 主权项 |
| LegalStatus              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 法律状态 |
| Language                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 正文语种 |
| FulltextPath             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 全文路径 |
| HasFulltext              | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文 |
| Type                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| CitedCount               | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 被引次数 |
| MetadataViewCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ThirdpartyLinkClickCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 第三方链接点击次数 |
| DownloadCount            | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| PublishDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 |
| PublishYear              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: Date, date |
| Priority                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 优先权 说明: 优先权 |
| CitedScore               | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| FulltextScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 除期刊外，其他资源该字段不赋值 |
| CoreScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 除期刊外，其他资源该字段不赋值 |
| YearScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore                | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |

### Periodical

| Field                    | Type              | Label    | Description                              |
| ------------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Title                    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, titles, 题, 题目, 篇名 说明: 第一位置为中文题名，第二位为英文题名，往后顺延为其他语种题名，如果没有中文，则第一位置为英文题目 |
| SingleTitle              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 单值题名 |
| Creator                  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者,中文作者及其对应拼音作者顺序一致，只有中文或只有英文作者没有该映射关系 |
| FirstCreator             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 第一作者 说明: 第一作者 |
| ScholarIdAuthor          | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 学者 Id,该字段与作者字段（Creator）映射，即使没有值，也用空值(&#34;&#34;)占位 |
| ScholarId                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 学者 Id,该字段与作者字段（Creator）映射，即使没有值，也用空值(&#34;&#34;)占位 |
| ForeignCreator           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文作者(作者拼音) |
| CreatorForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, a, creaters, author, authors, 人, 作者, 著者 说明: 作者检索字段(只用于检索) |
| OrganizationNorm         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 规范机构名 |
| OrganizationNew          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 最新机构名,当前和规范机构名值一致，今后可能会整理最新机构名 |
| OriginalOrganization     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 原机构名(作者发文时的机构名)，展示用 |
| OrganizationForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 作者单位, 机构, org, 单位, 机构名称, Organization 说明: 机构检索字段(只用于检索) |
| OriginalClassCode        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 原文分类号（聚类，显示），期刊论文都是原文分类号，存放在[orig_classcode]字段，[class_code]全部空值 |
| MachinedClassCode        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 存放[auto_classCode]，机标分类号 |
| ClassCodeForSearch       | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: false, 多值: true 别名: 分类号, clc, 分, 分类, c, 学科分类, 中图分类号 说明: 原文分类号检索字段(只用于检索 |
| PeriodicalClassCode      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 刊分类号 |
| ContentSearch            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索 |
| Keywords                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词,期刊论文都是原文关键词，存放在[orig_keys]、[trans_keys]字段，[keywords]全部空值 |
| ForeignKeywords          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文关键词 |
| MachinedKeywords         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 机标关键词 |
| KeywordForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段(只用于检索) |
| Abstract                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 第一位置为中文摘要，第二位为外文文摘。如果没有中文，则第一位置为外文摘要 |
| CitedCount               | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| PeriodicalId             | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 期刊 ID |
| PeriodicalTitleForSearch | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 刊名, 期刊名称/刊名, source, 出处, 文献来源, 期刊名称 说明: 刊名,用于检索。该字段为 CopyField，源于 PeriodicalTitle |
| PeriodicalTitle          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 刊名,第一位置为中文刊名，第二位位置为拼音刊名(有中文刊名时存在)，第三位置为英文刊名，第四位其他语种刊名(韩文) |
| SourceDB                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 来源数据库 |
| SingleSourceDB           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 来源数据库 说明: 单值来源数据库 |
| IsOA                     | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否 OA 论文 |
| Fund                     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 基金 说明: 基金 |
| PublishDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 出版时间(原文) |
| MetadataOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文文摘上网日期 |
| FulltextOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文全文上网日期 |
| ServiceMode              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 全文服务模式,0:没版权，1：有版权 |
| HasFulltext              | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文,0：没全文，1：有全文 |
| PublishYear              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 别名: 年份, Date, date 说明: 出版年,和出版时间统一，聚类使用，数据源提供了该字段 |
| Issue                    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 期, 期刊—期 说明: 期 |
| Volum                    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 卷 说明: 卷 |
| Page                     | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页码 |
| PageNo                   | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| Column                   | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 栏目名称,第一位置为中文栏目，第二位为外文栏目。 |
| CorePeriodical           | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: 核心 说明: 核心期刊收录 |
| FulltextPath             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 全文路径 |
| DOI                      | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: DOI |
| AuthorOrg                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 作者机构字段,值为：author1:org1;author2:org2;中英文作者都有，中文作者，优先匹配中文机构，英文作者优先匹配英文机构 |
| ThirdPartyUrl            | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 第三方链接字段,为：db1:url1,id1;db2:url2,id2 |
| Language                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 语种 说明: 语种 |
| ISSN                     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: ISSN |
| CN                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: CN |
| SequenceInIssue          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 期内论文次序 |
| MetadataViewCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ThirdpartyLinkClickCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 第三方链接点击次数 |
| DownloadCount            | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| PrePublishVersion        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 优先出版论文版本号 |
| PrePublishGroupId        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 优先出版论文多版本唯一标识 |
| PublishStatus            | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 出版状态 说明: 论文出版状态 |
| Type                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| CitedScore               | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| YearScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore                | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| FulltextScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |
| ProjectId                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 项目 Id |
| FundGroupName            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 基金项目名 |
| ProjectGrantNo           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 项目编号 |
| IsThirdService           | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否提供全文权限给第三方 |
| LastModifiedTime         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 最后修改时间 |

### Standard

| Field                | Type              | Label    | Description                              |
| -------------------- | ----------------- | -------- | ---------------------------------------- |
| Id                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| StandardNO           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 标准编号 说明: 标准编号,用于模糊检索 |
| Title                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, name, 名称, 标准名称 说明: 第一位置为中文题名，第二位为英文题名，往后顺延为其他语种题名，如果没有中文，则第一位置为英文题目 |
| DraftsComp           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 作者单位, 起草单位, organization, draftingcommittee 说明: 起草单位 |
| ICSCode              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 国际标准分类号 说明: 国际标准分类号 |
| CCSCode              | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 中国标准分类号 |
| IssueOrganization    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 发布单位 说明: 发布单位 |
| Publisher            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 出版单位 |
| Status               | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 标准状态 |
| ContentSearch        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索（缺省字段检索） |
| Keywords             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词 |
| ForeignKeywords      | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文关键词 |
| KeywordForSearch     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段(只用于检索) |
| Abstract             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 摘要 |
| CitedCount           | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 被引次数 |
| SourceDB             | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 来源数据库 |
| SingleSourceDB       | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 来源数据库 |
| IssueDate            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 日期 说明: 发布时间 |
| PublishDate          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 发布日期, 出版时间 说明: 发布时间 |
| PublishYear          | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: date, Date 说明: 发布年 |
| StandardType         | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 标准类型 |
| StandardOrganization | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 标准组织 |
| IsForce              | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 强制性标准 |
| FulltextPath         | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 全文路径 |
| HasFulltext          | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文 |
| IssueYear            | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份 |
| Language             | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 正文语种 |
| TechnicalCommittee   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 归口单位 |
| CiteStandard         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用标准 |
| AdoptStandard        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 采用标准 |
| OldStandard          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 被当前标准替代的旧标准 |
| NewStandard          | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 替代当前标准的新标准 |
| Type                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| OriginalId           | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 第三方数据的标准 Id,根据此 Id 链接到第三方地址 |
| StateCode            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 国家 说明: 国别代码 |
| ApplyDate            | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 实施日期 |
| PageNo               | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| MetadataViewCount    | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| DownloadCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 下载次数 |
| ExportCount          | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| CitedScore           | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore        | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore            | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| Price                | [double](#double) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 目前单指质检出版社的全文下载价格 |
| FulltextScore        | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### Thesis

| Field                    | Type              | Label    | Description                              |
| ------------------------ | ----------------- | -------- | ---------------------------------------- |
| Id                       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 唯一检索的 ID 字段 |
| Type                     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 类型 说明: 资源类型(资源聚类时使用) |
| Title                    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 题名, 标题, t, titles, 题, 题目, 篇名 说明: 第一位置为中文题名，第二位为英文题名，往后顺延为其他语种题名，如果没有中文，则第一位置为英文题目 |
| Creator                  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 作者,中文作者及其对应拼音作者顺序一致，只有中文或只有英文作者没有该映射关系 |
| CreatorForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 创作者, a, creaters, author, authors, 人, 作者, 著者 说明: 作者检索字段(只用于检索) |
| OrganizationNorm         | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 规范机构名 |
| OrganizationNew          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 最新机构名,当前和规范机构名值一致，今后可能会整理最新机构名 |
| OriginalOrganization     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 授予单位 说明: 原机构名(作者发文时的机构名)，展示用 |
| OrganizationForSearch    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 作者单位, 学位授予单位, 学校, school 说明: 机构检索字段(只用于检索) |
| ClassCode                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 分类号, clc, 分, 分类, c, 原文中图分类号 说明: 分类号（聚类，显示） |
| MachinedClassCode        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 存放[auto_classcode]，机标分类号 |
| ClassCodeForSearch       | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: false, 多值: true 别名: 中图分类号, 学科分类 说明: 原文分类号检索字段(只用于检索 |
| ContentSearch            | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 全部 说明: 多字段内容检索 |
| Keywords                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词,期刊论文都是原文关键词，存放在[orig_keys]、[trans_keys]字段，[keywords]全部空值 |
| ForeignKeywords          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 外文关键词 |
| MachinedKeywords         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 机标关键词 |
| KeywordForSearch         | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: false, 多值: true 别名: 关键词, k, Keyword, 词, 关键字, 主题词 说明: 关键词检索字段(只用于检索) |
| Abstract                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 摘要, b, abstracts, 概, 概要, 概述, 简述, 文摘 说明: 第一位置为中文摘要，第二位为外文文摘。如果没有中文，则第一位置为外文摘要 |
| CitedCount               | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| SourceDB                 | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 来源数据库 |
| PublishDate              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 学位授予时间, 出版时间 说明: 出版时间(原文) |
| MetadataOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文文摘上网日期 |
| FulltextOnlineDate       | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 论文全文上网日期 |
| ServiceMode              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 全文服务模式,0:没版权，1：有版权 |
| HasFulltext              | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文,0：没全文，1：有全文 |
| PublishYear              | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 别名: 年份, Date, date 说明: 出版年,和出版时间统一，聚类使用，数据源提供了该字段 |
| PageNo                   | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 页数 |
| FulltextPath             | [string](#string) |          | 可检索: false, 可聚类: false, 可取值: true, 多值: false 说明: 全文路径 |
| DOI                      | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: DOI |
| Degree                   | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 学位, degree, 授予学位 说明: 授予学位 |
| Language                 | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 语种 说明: 语种 |
| AuthorOrg                | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: AuthorOrg 字段（为开发方便，临时字段） |
| MajorCode                | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 专业代码 |
| Major                    | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 专业, authorsubject, 学科专业 说明: 学科专业 |
| ThirdPartyUrl            | [string](#string) | repeated | 可检索: false, 可聚类: false, 可取值: true, 多值: true 说明: 第三方链接字段,为：db1:url1,id1;db2:url2,id2 |
| Tutor                    | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 别名: teachername, teacher, 导师 说明: 导师 |
| Region                   | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 学校所在地 |
| MetadataViewCount        | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 文摘阅读次数 |
| ThirdpartyLinkClickCount | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 第三方链接点击次数 |
| DownloadCount            | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: false, 多值: false 别名: 下载量 说明: 下载次数 |
| ExportCount              | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 说明: 导出数 |
| FilterCondition          | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 保存指定字段中为空的字段名 |
| HasCatolog               | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有目录 |
| SingleSourceDB           | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 来源数据库 说明: 单值数据库来源 |
| CitedScore               | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore                | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| IsThirdService           | [bool](#bool)     |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否提供全文权限给第三方 |
| LastModifiedTime         | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 最后修改时间 |
| FulltextScore            | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore                | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |

### Video

| Field           | Type              | Label    | Description                              |
| --------------- | ----------------- | -------- | ---------------------------------------- |
| Id              | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: general |
| Title           | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 别名: 标题 说明: 视频名称 |
| FileType        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 文件类型 |
| Creator         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 名师（主讲人） |
| Organization    | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 机构（主讲人单位） |
| VideoSID        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false |
| Keywords        | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 关键词 |
| PublishYear     | [int32](#int32)   |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 别名: 时间 说明: 录制年代 |
| PublishDate     | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 别名: 出版时间 说明: 录制时间 |
| Duration        | [string](#string) |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 时长 |
| Clarity         | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 清晰度 |
| CaptionType     | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 字幕类型 |
| SourceName      | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 频道 |
| VideoClassCode  | [string](#string) | repeated | 可检索: true, 可聚类: true, 可取值: true, 多值: true 说明: 视频分类 |
| Series          | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 系列 |
| HasLecturesDown | [bool](#bool)     |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 是否有讲义 |
| SpecialName     | [string](#string) | repeated | 可检索: true, 可聚类: false, 可取值: true, 多值: true 说明: 专题名称 |
| Type            | [string](#string) |          | 可检索: true, 可聚类: true, 可取值: true, 多值: false 说明: 资源类型(资源聚类时使用) |
| CitedScore      | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 引用打分 |
| DownloadScore   | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 下载打分 |
| YearScore       | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 发布年份打分 |
| TypeScore       | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 类型打分 |
| CitedCount      | [int32](#int32)   |          | 可检索: true, 可聚类: false, 可取值: false, 多值: false 别名: 被引频次 说明: 被引次数 |
| FulltextScore   | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: 是否有全文打分，万方全文：60 分，免费或原文传递：20 分，无：0 分 |
| CoreScore       | [float](#float)   |          | 可检索: true, 可聚类: false, 可取值: true, 多值: false 说明: Sci 或 ei 35，pku20，nju20，istic10 |