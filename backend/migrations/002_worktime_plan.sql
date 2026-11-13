-- 存量部署升级：plans 增加工时制口径两列；旧数据保持 NULL，运行时回退到按份数预算的 Neyman 分配。
-- 新库由 SQLAlchemy 元数据直接建表，本脚本仅面向已有数据的 MySQL 8 库，执行前请备份。
ALTER TABLE plans
  ADD COLUMN stratum_costs JSON NULL,
  ADD COLUMN total_hours INT NULL;
-- 兼容性说明：
-- 1. stratum_costs / total_hours 同时为 NULL 的计划视为旧份数计划，预算仍取自 budget。
-- 2. 新工时计划两列同时非空：stratum_costs 存 {风险层键: 单份耗时}，total_hours 存总复核工时。
-- 3. 历史 runs.result 为不可变 JSON 快照，不回填新字段；旧运行继续展示份数口径。
