from pydantic import BaseModel,Field,model_validator
from ..constants.enums import Stratum
class PlanCreate(BaseModel):
 name:str=Field(min_length=2,max_length=180)
 lot_ids:list[str]=Field(min_length=1,max_length=30)
 target_detection:float=Field(default=.95,ge=0,le=1,allow_inf_nan=False)
 budget:int=Field(default=480,ge=1,le=5000)
 seed:int=Field(default=20261112,ge=0,le=2147483647)
 # 工时制口径：两字段同时提供即按总工时与各层单份耗时分配；为空则沿用份数预算。
 stratum_costs:dict[str,int]|None=Field(default=None)
 total_hours:int|None=Field(default=None,ge=1,le=10000000)
 @model_validator(mode="after")
 def unique_lots(self):
  if len(set(self.lot_ids))!=len(self.lot_ids):raise ValueError("批次不能重复选择")
  return self
 @model_validator(mode="after")
 def worktime_fields(self):
  if (self.stratum_costs is None)!=(self.total_hours is None):
   raise ValueError("各层单份耗时与总工时必须同时提供或同时省略")
  if self.stratum_costs is not None:
   valid={s.value for s in Stratum}
   if not self.stratum_costs or any(k not in valid for k in self.stratum_costs):
    raise ValueError("单份耗时的风险层键非法")
   if any(not isinstance(v,int) or not 1<=v<=1000 for v in self.stratum_costs.values()):
    raise ValueError("各层单份耗时须为1至1000的整数")
  return self
