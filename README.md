# lixiang-store-skill

> 查询理想汽车全国 1300+ 家门店信息的命令行工具与 WorkBuddy Skill。

数据源: 理想汽车官网公开接口 `https://www.lixiang.com/saos-store-web/tur_store/v1-0/service-centers`

## ✨ 功能特性

- 🚀 一次性拉取全国 1353+ 家理想门店数据
- 🎯 多维度过滤: 省 / 市 / 区 / 门店类型 / 状态 / 关键字 / 车型 / 附近坐标
- 📍 经纬度附近查询, 支持 Haversine 距离计算与排序
- 📦 多种输出: 人类可读文本 / JSON / CSV
- ⚡ 10 分钟本地缓存, 避免重复请求
- 🐍 纯 Python 标准库实现, 无第三方依赖
- 🧩 可作为 WorkBuddy Skill 被对话调用

## 📦 安装

### 方式 1: 作为 WorkBuddy Skill 安装

```bash
git clone https://github.com/chensjfish/lixiang-store-skill.git ~/.workbuddy/skills/lixiang-stores
```

### 方式 2: 仅下载脚本

```bash
curl -O https://raw.githubusercontent.com/chensjfish/lixiang-store-skill/main/scripts/lixiang_stores.py
python lixiang_stores.py --list-provinces
```

### 依赖

- Python 3.6+

无需 `pip install` 任何包。

## 🚀 快速开始

```bash
# 列出所有省份
python scripts/lixiang_stores.py --list-provinces

# 查询北京所有零售中心
python scripts/lixiang_stores.py --city 北京 --type RETAIL

# 关键字搜索"万象城"
python scripts/lixiang_stores.py --keyword 万象城

# 查询北京天安门附近 10km 内的门店
python scripts/lixiang_stores.py --near 39.9,116.3 --radius 10

# 查询可试驾理想 L9 的门店
python scripts/lixiang_stores.py --series 理想L9 --limit 10

# 导出广东省全部门店为 CSV
python scripts/lixiang_stores.py --province 广东 --output csv > guangdong.csv

# 导出上海所有交付中心为 JSON (自定义字段)
python scripts/lixiang_stores.py --city 上海 --type DELIVER --output json \
  --fields id,name,address,telephone,lat,lng
```

## 📚 参数说明

### 过滤参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--province` | 省份名 | `--province 广东` |
| `--city` | 城市名 | `--city 深圳` |
| `--district` | 区/县名 | `--district 南山` |
| `--type` | 门店类型代码 | `--type RETAIL` |
| `--status` | 门店状态代码 | `--status INBUSINESS` |
| `--keyword` | 关键字(匹配门店名/地址) | `--keyword 万象城` |
| `--series` | 车型名 | `--series 理想L9` |
| `--near` | 经纬度, 配合 `--radius` | `--near 39.9,116.3` |
| `--radius` | 附近查询半径(km), 默认 10 | `--radius 20` |
| `--limit` | 限制返回数量 | `--limit 5` |

### 输出参数

| 参数 | 说明 |
|------|------|
| `--output text` | 人类可读文本(默认) |
| `--output json` | JSON 数组 |
| `--output csv` | CSV 表格 |
| `--fields a,b,c` | 自定义字段(仅对 json/csv 有效) |

### 列表类参数

| 参数 | 说明 |
|------|------|
| `--list-provinces` | 列出所有省/直辖市/自治区 |
| `--list-cities <province>` | 列出指定省下所有城市 |
| `--list-types` | 门店类型分布统计 |
| `--list-statuses` | 门店状态分布统计 |

### 缓存参数

| 参数 | 说明 |
|------|------|
| `--force-refresh` | 忽略缓存, 重新请求 API |
| `--no-cache` | 不读取缓存(但仍会写入) |

### 门店类型枚举

| 代码 | 中文 |
|------|------|
| RETAIL | 零售中心 |
| DELIVER | 交付中心 |
| AFTERSALE | 售后中心 |
| SPRAY | 喷涂中心 |
| UNION | 综合门店 |
| TEMPORARY_DELIVER | 临时交付 |
| TEMPORARY_AFTERSALE_SUPPORT | 临时售后支持 |

### 门店状态枚举

| 代码 | 中文 |
|------|------|
| INBUSINESS | 营业中 |
| INCONSTRUCTION | 筹建中 |
| CLOSED | 已关闭 |

## 📁 项目结构

```
lixiang-store-skill/
├── SKILL.md                      # WorkBuddy Skill 入口文件
├── scripts/
│   └── lixiang_stores.py         # 主脚本
├── references/
│   └── api-reference.md          # API 参考文档
├── examples/
│   ├── list_provinces.txt        # 示例输出
│   ├── beijing_retail.txt        # 示例输出
│   └── shanghai_delivery.csv     # 示例 CSV
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 📖 示例输出

### 文本输出

```
共找到 1 家门店:

[RBJS01] 理想汽车北京华熙LIVE零售中心
  类型: 零售中心  状态: 营业中
  地址: 北京北京海淀 北京市海淀区复兴路69号华熙LIVE五棵松购物中心B1层101号
  电话: 18629466019
  营业时间: 10:00-22:00
  开业日期: 2019年5月1日上午10:00
  坐标: (39.915065, 116.283664)
  距离: 2.18 km
  可试驾车型: 理想i6, 理想i8, 理想MEGA, 理想L6, 理想L8, 理想L9
```

### CSV 输出

```csv
id,name,type,status,provinceName,cityName,countyName,address,telephone,openingHours,openedAt,lat,lng
DSHA04,理想汽车上海浦东交付中心,DELIVER,INBUSINESS,上海,上海,浦东,上海市浦东申江南路3588号,18862708111,9:00-18:00,,31.10248,121.64996
```

## 🧩 作为 WorkBuddy Skill 使用

安装到 `~/.workbuddy/skills/lixiang-stores` 后, 可在 WorkBuddy 对话中直接触发:

- "北京有哪些理想汽车门店?"
- "深圳南山区附近 5 公里内的理想门店"
- "理想 L9 在哪些门店可以试驾?"
- "导出上海所有理想交付中心的 CSV"
- "理想汽车门店最多的省份是哪个?"

详见 `SKILL.md`。

## ⚠️ 免责声明

- 本工具调用的是理想汽车官网公开接口, 仅用于学习与个人参考
- 门店信息以理想汽车官网实时数据为准
- 请勿用于商业爬取或高频请求场景
- 本项目与理想汽车公司无任何关联

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)
