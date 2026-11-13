from sqlalchemy import String,JSON,Double
from sqlalchemy.orm import Mapped,mapped_column
from .common import RecordMixin
from ..config.database import Base
class SamplingPlan(RecordMixin,Base):
 __tablename__="plans"
 name:Mapped[str]=mapped_column(String(180),unique=True)
 lot_ids:Mapped[list]=mapped_column(JSON)
 target_detection:Mapped[float]=mapped_column(Double)
 budget:Mapped[int]
 seed:Mapped[int]
 # 工时制口径：stratum_costs 为 {风险层键: 单份耗时}，total_hours 为总复核工时。
 # 旧数据两列为 NULL，运行时回退到按份数预算的 Neyman 分配，保证升级后原计划口径不变。
 stratum_costs:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 total_hours:Mapped[int|None]=mapped_column(nullable=True)
