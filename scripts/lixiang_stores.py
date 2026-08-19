#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想汽车门店查询脚本

数据源: https://www.lixiang.com/saos-store-web/tur_store/v1-0/service-centers
返回理想汽车全国 1300+ 家门店(零售中心/交付中心/售后中心/喷涂中心等)

特性:
- 一次性拉取全部门店数据, 在本地做过滤, 无需多次请求
- 支持按 省/市/区/类型/状态/关键字/门店类别 过滤
- 支持按经纬度查询附近门店(指定半径)
- 支持导出为 JSON / CSV
- 内置 10 分钟本地缓存, 避免重复请求
- 仅使用 Python 标准库, 无第三方依赖

用法:
    python lixiang_stores.py --province 北京
    python lixiang_stores.py --city 上海 --type RETAIL
    python lixiang_stores.py --near 39.9,116.3 --radius 10
    python lixiang_stores.py --keyword 万象城 --output csv
    python lixiang_stores.py --list-provinces
    python lixiang_stores.py --list-cities 广东
    python lixiang_stores.py --category aftersale
"""

import argparse
import csv
import io
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

API_URL = "https://www.lixiang.com/saos-store-web/tur_store/v1-0/service-centers"
CACHE_TTL_SECONDS = 600  # 10 分钟


def default_cache_dir():
    """返回跨平台的默认缓存目录, 可用环境变量 LIXIANG_STORES_CACHE_DIR 覆盖"""
    env = os.environ.get("LIXIANG_STORES_CACHE_DIR")
    if env:
        return env
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "lixiang-stores")
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Caches", "lixiang-stores")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "lixiang-stores")


CACHE_DIR = default_cache_dir()

# 门店类型中文映射
TYPE_LABELS = {
    "RETAIL": "零售中心",
    "DELIVER": "交付中心",
    "AFTERSALE": "售后中心",
    "SPRAY": "喷涂中心",
    "UNION": "综合门店",
    "TEMPORARY_DELIVER": "临时交付",
    "TEMPORARY_AFTERSALE_SUPPORT": "临时售后支持",
}

# 状态中文映射
STATUS_LABELS = {
    "INBUSINESS": "营业中",
    "INCONSTRUCTION": "筹建中",
    "CLOSED": "已关闭",
}

# 门店类别(业务口径)筛选规则: 综合门店(UNION)同时属于销售/售后/交付
CATEGORY_RULES = {
    "sales": {"RETAIL", "UNION"},                                                # 销售门店
    "aftersale": {"AFTERSALE", "SPRAY", "TEMPORARY_AFTERSALE_SUPPORT", "UNION"}, # 售后门店
    "delivery": {"DELIVER", "TEMPORARY_DELIVER", "UNION"},                       # 交付门店
}


def ensure_cache_dir():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception:
        pass


def cache_path():
    return os.path.join(CACHE_DIR, "stores.json")


def load_cache():
    p = cache_path()
    if not os.path.exists(p):
        return None
    try:
        mtime = os.path.getmtime(p)
        if time.time() - mtime > CACHE_TTL_SECONDS:
            return None
        with open(p, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("data", [])
    except Exception:
        return None


def save_cache(data):
    try:
        ensure_cache_dir()
        with open(cache_path(), "w", encoding="utf-8") as f:
            json.dump({"fetched_at": datetime.now().isoformat(), "data": data}, f, ensure_ascii=False)
    except Exception:
        pass


def fetch_stores(force_refresh=False):
    """从缓存或 API 获取门店列表"""
    if not force_refresh:
        cached = load_cache()
        if cached is not None:
            return cached, True  # 第二个值表示是否来自缓存

    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; lixiang-stores-skill/1.0)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        # 网络失败时退回过期缓存
        p = cache_path()
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                return payload.get("data", []), True
            except Exception:
                pass
        raise RuntimeError(f"请求理想门店接口失败: {e}")
    except Exception as e:
        raise RuntimeError(f"解析响应失败: {e}")

    data = payload.get("data", [])
    save_cache(data)
    return data, False


def haversine_km(lat1, lon1, lat2, lon2):
    """计算两个经纬度坐标之间的距离(km), 使用 Haversine 公式"""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def filter_stores(stores, args):
    """按命令行参数过滤门店"""
    result = stores

    if args.province:
        result = [s for s in result if s.get("provinceName") == args.province]
    if args.city:
        result = [s for s in result if s.get("cityName") == args.city]
    if args.district:
        result = [s for s in result if s.get("countyName") == args.district]
    if args.type:
        result = [s for s in result if s.get("type") == args.type]
    if args.category:
        allowed = CATEGORY_RULES[args.category]
        result = [s for s in result if s.get("type") in allowed]
    if args.status:
        result = [s for s in result if s.get("status") == args.status]
    if args.keyword:
        kw = args.keyword.lower()
        result = [
            s for s in result
            if kw in (s.get("name") or "").lower()
            or kw in (s.get("address") or "").lower()
        ]
    if args.series:
        result = [
            s for s in result
            if args.series in (s.get("driveCarSeriesName") or [])
            or args.series in (s.get("exhibitionCarSeriesName") or [])
        ]
    if args.near:
        try:
            lat_str, lng_str = args.near.split(",")
            lat, lng = float(lat_str), float(lng_str)
        except Exception:
            raise ValueError("--near 参数格式应为 'lat,lng', 例如 '39.9,116.3'")
        radius = args.radius if args.radius is not None else 10.0
        with_distance = []
        for s in result:
            slat = s.get("lat")
            slng = s.get("lng")
            if slat is None or slng is None:
                continue
            dist = haversine_km(lat, lng, slat, slng)
            if dist <= radius:
                s_with_d = dict(s)
                s_with_d["_distance_km"] = round(dist, 2)
                with_distance.append(s_with_d)
        with_distance.sort(key=lambda x: x["_distance_km"])
        result = with_distance
    return result


def pick_fields(store, fields):
    """从门店对象中挑选指定字段"""
    return {f: store.get(f) for f in fields}


def render_store(store):
    """人类可读的单门店渲染"""
    type_label = TYPE_LABELS.get(store.get("type"), store.get("type"))
    status_label = STATUS_LABELS.get(store.get("status"), store.get("status"))
    lines = [
        f"[{store.get('id')}] {store.get('name')}",
        f"  类型: {type_label}  状态: {status_label}",
        f"  地址: {store.get('provinceName')}{store.get('cityName')}{store.get('countyName')} {store.get('address')}",
        f"  电话: {store.get('telephone')}",
        f"  营业时间: {store.get('openingHours')}",
        f"  开业日期: {store.get('openedAt')}",
        f"  坐标: ({store.get('lat')}, {store.get('lng')})",
    ]
    if store.get("_distance_km") is not None:
        lines.append(f"  距离: {store['_distance_km']} km")
    drive = store.get("driveCarSeriesName") or []
    if drive:
        lines.append(f"  可试驾车型: {', '.join(drive)}")
    return "\n".join(lines)


def output_text(stores, args):
    if not stores:
        print("未找到匹配的门店")
        return
    print(f"共找到 {len(stores)} 家门店:\n")
    for s in stores:
        print(render_store(s))
        print()


def output_json(stores, args, fields=None):
    data = stores
    if fields:
        data = [pick_fields(s, fields) for s in stores]
    print(json.dumps(data, ensure_ascii=False, indent=2))


def output_csv(stores, args, fields=None):
    if not stores:
        print("(空)")
        return
    if not fields:
        # 默认字段集
        fields = [
            "id", "name", "type", "status",
            "provinceName", "cityName", "countyName", "address",
            "telephone", "openingHours", "openedAt",
            "lat", "lng",
        ]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    for s in stores:
        row = []
        for f in fields:
            v = s.get(f)
            if isinstance(v, list):
                v = "|".join(str(x) for x in v)
            row.append(v)
        writer.writerow(row)
    print(buf.getvalue(), end="")


def list_provinces(stores):
    seen = {}
    for s in stores:
        p = s.get("provinceName")
        if p and p not in seen:
            seen[p] = s.get("provinceId")
    print(f"共 {len(seen)} 个省/直辖市/自治区:")
    for name in sorted(seen.keys()):
        print(f"  - {name} (id={seen[name]})")


def list_cities(stores, province):
    cities = {}
    for s in stores:
        if s.get("provinceName") == province:
            c = s.get("cityName")
            if c and c not in cities:
                cities[c] = s.get("cityId")
    if not cities:
        print(f"未找到省份: {province}")
        return
    print(f"{province} 共 {len(cities)} 个城市:")
    for name in sorted(cities.keys()):
        print(f"  - {name} (id={cities[name]})")


def list_types(stores):
    counts = {}
    for s in stores:
        t = s.get("type")
        counts[t] = counts.get(t, 0) + 1
    print("门店类型分布:")
    for t, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  - {t} ({TYPE_LABELS.get(t, t)}): {c}")


def list_statuses(stores):
    counts = {}
    for s in stores:
        st = s.get("status")
        counts[st] = counts.get(st, 0) + 1
    print("门店状态分布:")
    for st, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  - {st} ({STATUS_LABELS.get(st, st)}): {c}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="理想汽车门店查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python lixiang_stores.py --province 北京\n"
               "  python lixiang_stores.py --city 上海 --type RETAIL\n"
               "  python lixiang_stores.py --near 39.9,116.3 --radius 10\n"
               "  python lixiang_stores.py --keyword 万象城 --output csv\n"
               "  python lixiang_stores.py --list-provinces\n"
               "  python lixiang_stores.py --list-cities 广东\n",
    )
    parser.add_argument("--province", help="按省份名过滤, 如 '广东'")
    parser.add_argument("--city", help="按城市名过滤, 如 '深圳'")
    parser.add_argument("--district", help="按区/县名过滤, 如 '南山'")
    parser.add_argument("--type", help="按门店类型过滤: RETAIL/DELIVER/AFTERSALE/SPRAY/UNION/TEMPORARY_DELIVER/TEMPORARY_AFTERSALE_SUPPORT")
    parser.add_argument("--category", choices=["sales", "aftersale", "delivery"], help="按门店类别过滤: sales=销售门店(RETAIL+UNION) / aftersale=售后门店(AFTERSALE+SPRAY+TEMPORARY_AFTERSALE_SUPPORT+UNION) / delivery=交付门店(DELIVER+TEMPORARY_DELIVER+UNION)")
    parser.add_argument("--status", help="按状态过滤: INBUSINESS/INCONSTRUCTION/CLOSED")
    parser.add_argument("--keyword", help="关键字搜索(匹配门店名或地址)")
    parser.add_argument("--series", help="按车型过滤, 如 '理想L9'")
    parser.add_argument("--near", help="按经纬度查询附近, 格式 'lat,lng', 如 '39.9,116.3'")
    parser.add_argument("--radius", type=float, default=10.0, help="附近查询半径(km), 默认 10")
    parser.add_argument("--limit", type=int, help="限制返回数量")
    parser.add_argument("--output", choices=["text", "json", "csv"], default="text", help="输出格式, 默认 text")
    parser.add_argument("--fields", help="自定义字段(以逗号分隔), 仅对 json/csv 有效")
    parser.add_argument("--list-provinces", action="store_true", help="列出所有省/直辖市/自治区")
    parser.add_argument("--list-cities", metavar="PROVINCE", help="列出指定省下的所有城市")
    parser.add_argument("--list-types", action="store_true", help="列出所有门店类型分布")
    parser.add_argument("--list-statuses", action="store_true", help="列出所有门店状态分布")
    parser.add_argument("--force-refresh", action="store_true", help="忽略缓存, 重新请求 API")
    parser.add_argument("--no-cache", action="store_true", help="不读取缓存(但仍会写入)")
    parser.add_argument("--cache-dir", help="自定义缓存目录, 覆盖默认路径")
    return parser


def main():
    global CACHE_DIR
    parser = build_parser()
    args = parser.parse_args()

    if args.cache_dir:
        CACHE_DIR = args.cache_dir

    try:
        stores, from_cache = fetch_stores(force_refresh=args.force_refresh or args.no_cache)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 列表类操作
    if args.list_provinces:
        list_provinces(stores)
        return
    if args.list_cities:
        list_cities(stores, args.list_cities)
        return
    if args.list_types:
        list_types(stores)
        return
    if args.list_statuses:
        list_statuses(stores)
        return

    # 过滤
    try:
        filtered = filter_stores(stores, args)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(2)

    if args.limit and args.limit > 0:
        filtered = filtered[: args.limit]

    # 字段处理
    fields = None
    if args.fields:
        fields = [f.strip() for f in args.fields.split(",") if f.strip()]

    # 输出
    if args.output == "json":
        output_json(filtered, args, fields)
    elif args.output == "csv":
        output_csv(filtered, args, fields)
    else:
        output_text(filtered, args)

    # 在 text 模式下补充缓存来源提示
    if args.output == "text" and not any([
        args.list_provinces, args.list_cities, args.list_types, args.list_statuses
    ]):
        src = "(来自缓存)" if from_cache else "(实时拉取)"
        print(f"\n数据源: {src}  共 {len(filtered)} 家匹配门店")


if __name__ == "__main__":
    main()
