# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [1.1.0] - 2026-08-19

### Added
- 新增 `--category` 门店类别筛选: `sales`(销售) / `aftersale`(售后) / `delivery`(交付)
- 综合门店(UNION) 同时属于销售/售后/交付三类

### Changed
- 移除 `triggered_when` 自动触发词, 改为仅通过 `/lixiang-stores` 显式触发

## [1.0.0] - 2026-08-18

### Added
- 首次发布
- 实现理想汽车门店 API 调用与本地缓存
- 支持按 省/市/区/类型/状态/关键字/车型 过滤
- 支持经纬度附近查询(Haversine 距离)
- 支持 text / json / csv 三种输出格式
- 支持自定义字段输出
- 提供 `--list-provinces` / `--list-cities` / `--list-types` / `--list-statuses` 列表统计
- 作为 Agent Skill / 独立命令行工具使用
