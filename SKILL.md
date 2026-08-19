---
name: lixiang-stores
version: 1.1.0
summary: 查询理想汽车全国 1300+ 家门店(零售/交付/售后/喷涂/综合)的信息, 支持省市区/类型/状态/关键字/坐标附近查询, 支持按门店类别(销售/售后/交付)筛选, 可导出 JSON/CSV
triggered_when:
  - 查询理想汽车门店
  - 理想汽车 4S 店 / 零售中心 / 交付中心 / 售后中心
  - 哪里有理想汽车门店
  - 理想汽车门店地址电话
  - 某城市/某地附近的理想门店
  - 理想汽车试驾车 / 试驾车型
  - 理想汽车销售门店 / 售后门店 / 交付门店
  - 导出理想汽车门店数据
  - Li Auto store / showroom / delivery center
  - lixiang store
---

# lixiang-stores Skill

查询理想汽车全国 1300+ 家门店信息, 数据源为理想汽车官网公开接口。

## 数据源

- API: `https://www.lixiang.com/saos-store-web/tur_store/v1-0/service-centers`
- 一次性返回全部门店 (约 1353 家), 在客户端做过滤
- 内置 10 分钟本地缓存, 避免重复请求

## 门店类型

| 代码 | 中文 |
|------|------|
| RETAIL | 零售中心 |
| DELIVER | 交付中心 |
| AFTERSALE | 售后中心 |
| SPRAY | 喷涂中心 |
| UNION | 综合门店 |
| TEMPORARY_DELIVER | 临时交付 |
| TEMPORARY_AFTERSALE_SUPPORT | 临时售后支持 |

## 门店状态

| 代码 | 中文 |
|------|------|
| INBUSINESS | 营业中 |
| INCONSTRUCTION | 筹建中 |
| CLOSED | 已关闭 |

## 门店类别(业务口径筛选)

按销售/售后/交付三类门店筛选, 用 `--category` 参数。注意: **综合门店(UNION) 同时属于三类**, 即"销售 + 售后 + 交付"三合一。

| 类别 | 参数值 | 包含的门店类型 |
|------|--------|----------------|
| 销售门店 | `sales` | 零售中心(RETAIL) + 综合门店(UNION) |
| 售后门店 | `aftersale` | 售后中心(AFTERSALE) + 喷涂中心(SPRAY) + 临时售后支持(TEMPORARY_AFTERSALE_SUPPORT) + 综合门店(UNION) |
| 交付门店 | `delivery` | 交付中心(DELIVER) + 临时交付(TEMPORARY_DELIVER) + 综合门店(UNION) |

## 字段说明

每条门店记录包含以下字段:

- `id`: 门店编码
- `name`: 门店名称
- `type`: 门店类型
- `status`: 门店状态
- `provinceName` / `cityName` / `countyName`: 省/市/区
- `provinceId` / `cityId` / `countyId`: 行政区划码
- `address`: 详细地址
- `telephone`: 电话
- `openingHours`: 营业时间
- `openedAt`: 开业日期
- `lat` / `lng`: 经纬度(原始坐标)
- `locations.baiduLat`/`baiduLng`: 百度地图坐标
- `locations.gdLat`/`gdLng`: 高德地图坐标
- `imgUrl`: 门店图片
- `isMetalSpray`: 是否支持钣喷(0/1)
- `driveCarSeriesName`: 可试驾车型列表
- `exhibitionCarSeriesName`: 在展车型列表
- `testDriveStatus`: 试驾状态(1=可试驾)
- `testDriveDesc`: 试驾说明
- `firstSaleCarArrival`: 首销车到店信息(部分门店)

## 调用方式

通过执行 `scripts/lixiang_stores.py` 完成, 使用 Python 3 标准库, 无第三方依赖。

```bash
python scripts/lixiang_stores.py [过滤参数] [输出参数]
```

## 过滤参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--province` | 省份名 | `--province 广东` |
| `--city` | 城市名 | `--city 深圳` |
| `--district` | 区/县名 | `--district 南山` |
| `--type` | 门店类型代码 | `--type RETAIL` |
| `--category` | 门店类别: sales/aftersale/delivery | `--category aftersale` |
| `--status` | 门店状态代码 | `--status INBUSINESS` |
| `--keyword` | 关键字(匹配门店名/地址) | `--keyword 万象城` |
| `--series` | 车型名 | `--series 理想L9` |
| `--near` | 经纬度, 配合 `--radius` | `--near 39.9,116.3 --radius 10` |
| `--radius` | 附近查询半径(km), 默认 10 | `--radius 20` |
| `--limit` | 限制返回数量 | `--limit 5` |

## 输出参数

| 参数 | 说明 |
|------|------|
| `--output text` | 人类可读文本(默认) |
| `--output json` | JSON 数组 |
| `--output csv` | CSV 表格 |
| `--fields a,b,c` | 自定义字段(仅对 json/csv 有效) |

## 列表类参数

| 参数 | 说明 |
|------|------|
| `--list-provinces` | 列出所有省/直辖市/自治区 |
| `--list-cities <province>` | 列出指定省下所有城市 |
| `--list-types` | 门店类型分布统计 |
| `--list-statuses` | 门店状态分布统计 |

## 缓存参数

| 参数 | 说明 |
|------|------|
| `--force-refresh` | 忽略缓存, 重新请求 API |
| `--no-cache` | 不读取缓存(但仍会写入) |
| `--cache-dir <dir>` | 自定义缓存目录, 覆盖默认路径 |

## 使用示例

```bash
# 列出所有省
python scripts/lixiang_stores.py --list-provinces

# 查询北京所有零售中心
python scripts/lixiang_stores.py --city 北京 --type RETAIL

# 查询全国售后门店(含综合门店)
python scripts/lixiang_stores.py --category aftersale

# 查询广东的销售门店(含综合门店)
python scripts/lixiang_stores.py --province 广东 --category sales

# 查询上海浦东交付中心, 输出 CSV
python scripts/lixiang_stores.py --city 上海 --district 浦东 --type DELIVER --output csv

# 查询深圳南山附近 10km 内的门店
python scripts/lixiang_stores.py --near 22.83,108.32 --radius 10 --limit 5

# 关键字搜索"万象城"
python scripts/lixiang_stores.py --keyword 万象城

# 查询可试驾理想 L9 的门店
python scripts/lixiang_stores.py --series 理想L9 --limit 10

# 导出广东省全部门店为 JSON
python scripts/lixiang_stores.py --province 广东 --output json > guangdong.json
```

## 典型对话触发

- "北京有哪些理想汽车门店?"
- "深圳南山区附近 5 公里内的理想门店"
- "理想 L9 在哪些门店可以试驾?"
- "导出上海所有理想交付中心的 CSV"
- "理想汽车门店最多的省份是哪个?"
- "查一下广州万象城有没有理想门店"
- "全国有多少理想汽车售后门店 / 销售门店 / 交付门店"

## 安装方法

```bash
# 方式 1: 克隆仓库
git clone https://github.com/chensjfish/lx.git
cd lx
python scripts/lixiang_stores.py --list-provinces

# 方式 2: 仅下载脚本
curl -O https://raw.githubusercontent.com/chensjfish/lx/main/scripts/lixiang_stores.py
python lixiang_stores.py --list-provinces
```

## 免责声明

- 本 skill 调用的是理想汽车官网公开接口, 仅用于学习与个人参考
- 门店信息以理想汽车官网实时数据为准
- 请勿用于商业爬取或高频请求场景
