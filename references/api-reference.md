# 理想汽车门店 API 参考

## 端点

```
GET https://www.lixiang.com/saos-store-web/tur_store/v1-0/service-centers
```

## 请求

| 项 | 值 |
|----|----|
| 方法 | GET |
| 协议 | HTTPS |
| 请求体 | 无 |
| 必需 Header | `User-Agent` (建议携带, 否则可能被拦截) |
| 可选 Header | `Accept: application/json` |

### 已知服务端支持的查询参数

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| `cityId` | int | `110100` | 按行政区划码过滤(城市级) |
| `type` | string | `RETAIL` | 按门店类型过滤 |

> 注: 实测 `provinceName` / `status` / `cityName` 等查询参数未生效, 需在客户端过滤。

### 已知不支持

- POST 方法: 返回 `{"code":2,"msg":"请在配置文件配置可访问域名"}`
- 分页: 接口一次性返回全部门店

## 响应

### 顶层结构

```json
{
  "data": [ <store>, ... ]
}
```

> 实测 `data` 数组中包含约 1353 条门店记录。

### 单门店字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 门店编码, 如 `RBJS18` |
| `name` | string | 门店名称 |
| `type` | string | 门店类型, 见下表 |
| `status` | string | 门店状态, 见下表 |
| `provinceId` | int | 省级行政区划码 |
| `provinceName` | string | 省名 |
| `cityId` | int | 市级行政区划码 |
| `cityName` | string | 城市名 |
| `countyId` | int | 区/县行政区划码 |
| `countyName` | string | 区/县名 |
| `address` | string | 详细地址 |
| `telephone` | string | 联系电话 |
| `openingHours` | string | 营业时间, 如 `10:00-22:00` |
| `openedAt` | string | 开业日期(格式不统一) |
| `lat` | float | 纬度 |
| `lng` | float | 经度 |
| `locations` | object | 各地图厂商坐标 |
| `locations.baiduLat` / `baiduLng` | float | 百度地图坐标 |
| `locations.gdLat` / `gdLng` | float | 高德地图坐标 |
| `imgUrl` | string | 门店图片 URL |
| `isMetalSpray` | int | 是否支持钣喷(0=否, 1=是) |
| `driveCarSeriesName` | string[] | 可试驾车型列表 |
| `exhibitionCarSeriesName` | string[] | 在展车型列表 |
| `testDriveStatus` | int | 试驾状态(1=可试驾) |
| `testDriveDesc` | string | 试驾说明(常为空) |
| `firstSaleCarArrival` | object? | 首销车到店信息(仅部分门店) |
| `firstSaleCarArrival.carSeriesCode` | string | 车系代码 |
| `firstSaleCarArrival.carSeriesName` | string | 车系名 |
| `firstSaleCarArrival.title` | string | 标题 |
| `firstSaleCarArrival.carModelGroups[]` | array | 车型分组 |
| `firstSaleCarArrival.carModelGroups[].carModelName` | string | 车型名 |
| `firstSaleCarArrival.carModelGroups[].carConfigs[]` | array | 配置列表 |
| `firstSaleCarArrival.carModelGroups[].carConfigs[].outerColorName` | string | 外观颜色 |
| `firstSaleCarArrival.carModelGroups[].carConfigs[].innerColorName` | string | 内饰颜色 |
| `firstSaleCarArrival.carModelGroups[].carConfigs[].outerImage` | string | 外观图 URL |
| `firstSaleCarArrival.carModelGroups[].carConfigs[].innerImage` | string | 内饰图 URL |

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

## 响应示例(单条)

```json
{
  "address": "北京市海淀区远大路1号新燕莎MALL【一】层【1113N，1115B】",
  "cityId": 110100,
  "cityName": "北京",
  "countyId": 110108,
  "countyName": "海淀",
  "driveCarSeriesName": ["理想i6", "理想i8", "理想MEGA", "理想L9"],
  "exhibitionCarSeriesName": ["理想i6", "理想i8", "理想MEGA", "理想L9"],
  "id": "RBJS18",
  "imgUrl": "https://p.ampmake.com/tur/20260311/rm/da7c9847-0221-47f4-bc32-656e7a2b49d4.png",
  "isMetalSpray": 0,
  "lat": 39.965345,
  "lng": 116.296396,
  "locations": {
    "baiduLat": 39.965345,
    "baiduLng": 116.296396,
    "gdLat": 39.959042,
    "gdLng": 116.290001
  },
  "name": "理想汽车北京世纪金源零售中心",
  "openedAt": "2022-07-21",
  "openingHours": "周一至周四10:00-21:00;周五至周日10:00-22:00",
  "provinceId": 110000,
  "provinceName": "北京",
  "status": "CLOSED",
  "telephone": "18515128123",
  "testDriveDesc": "",
  "testDriveStatus": 1,
  "type": "RETAIL"
}
```

## 数据规模

- 门店总数: ~1353
- 省份覆盖: 31 (除港澳台外)
- 类型分布(实测):
  - RETAIL: 577
  - AFTERSALE: 284
  - SPRAY: 258
  - DELIVER: 136
  - TEMPORARY_AFTERSALE_SUPPORT: 67
  - UNION: 30
  - TEMPORARY_DELIVER: 1
