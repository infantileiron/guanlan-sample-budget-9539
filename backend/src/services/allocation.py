import math
from .hypergeometric import estimated_defects,minimum_sample,miss_probability
from .neyman import allocate
from .worktime import allocate_worktime

def _summarize_strata(lots,target):
 strata={}
 for lot in lots:
  group=strata.setdefault(lot["stratum"],{"N":0,"D":0,"expected_errors":0.,"lot_count":0})
  group["N"]+=lot["size"]
  group["D"]+=estimated_defects(lot["size"],lot["estimated_error_rate"])
  group["expected_errors"]+=lot["size"]*lot["estimated_error_rate"]
  group["lot_count"]+=1
 for key,group in strata.items():
  group["stratum"]=key
  group["estimated_rate"]=group["expected_errors"]/group["N"]
  group["minimum"]=minimum_sample(group["N"],group["D"],target)
  group["weight"]=group["N"]*math.sqrt(group["estimated_rate"]*(1-group["estimated_rate"]))
 return strata

def _infeasible(strata,extra):
 impossible=[k for k,g in strata.items() if g["minimum"] is None]
 capacity=sum(g["N"] for g in strata.values())
 if impossible:
  reason="假设差错数D=0，非零检出目标不可达："+", ".join(impossible)
 elif extra=="count":
  reason="预算低于各风险层目标检出率的精确最小样本量之和"
 else:
  reason="总工时低于各风险层目标检出率所需最小工时之和"
 return impossible,capacity,reason

def calculate(lots,target,budget,stratum_costs=None,total_hours=None):
 strata=_summarize_strata(lots,target)
 impossible,capacity,base_reason=_infeasible(strata,"hours" if total_hours is not None else "count")
 ordered=[strata[k] for k in sorted(strata)]
 if total_hours is None:
  return _calculate_by_count(strata,ordered,target,budget,impossible,capacity,base_reason)
 return _calculate_by_hours(strata,ordered,target,stratum_costs,total_hours,impossible,capacity,base_reason)

def _calculate_by_count(strata,ordered,target,budget,impossible,capacity,base_reason):
 required=None if impossible else sum(g["minimum"] for g in strata.values())
 reason=base_reason if impossible else "预算低于各风险层目标检出率的精确最小样本量之和" if budget<required else "预算超过所选档案总容量" if budget>capacity else ""
 result={"allocation_mode":"count","feasible":not bool(reason),"reason":reason,
  "required_budget":required,"budget":budget,"target":target,"capacity":capacity,
  "strata":ordered,
  "assumption":"每个风险层汇总所选批次，D=sum ceil(N_lot*p_lot)；目标按风险层判断，不保证每批分别达标。层内文档等概率、无放回抽取。"}
 if reason:return result
 quotas,ideals=allocate({k:g["N"] for k,g in strata.items()},{k:g["weight"] for k,g in strata.items()},budget,{k:g["minimum"] for k,g in strata.items()})
 for key,group in strata.items():
  group["quota"]=quotas[key];group["ideal"]=ideals[key]
  group["miss_probability"]=miss_probability(group["N"],group["D"],quotas[key])
  group["detection_probability"]=1-group["miss_probability"]
  group["guaranteed"]=group["D"]>0 and quotas[key]>group["N"]-group["D"]
 return result

def _calculate_by_hours(strata,ordered,target,stratum_costs,total_hours,impossible,capacity,base_reason):
 # 未配置单份耗时的风险层不允许进入工时计划，避免隐式按 0 工时抽样。
 missing=[k for k in sorted(strata) if k not in stratum_costs]
 if missing and not impossible:
  reason="以下风险层未设置单份耗时："+", ".join(missing)
  return {"allocation_mode":"worktime","feasible":False,"reason":reason,
   "required_hours":None,"total_hours":total_hours,"target":target,"capacity":capacity,
   "budget":None,"required_budget":None,"strata":ordered,
   "assumption":"工时制：先满足各风险层检出目标，再在总工时内最大化最低检出率，余时允许闲置。"}
 if impossible:
  result={"allocation_mode":"worktime","feasible":False,"reason":base_reason,
   "required_hours":None,"total_hours":total_hours,"target":target,"capacity":capacity,
   "budget":None,"required_budget":None,"strata":ordered,
   "assumption":"工时制：先满足各风险层检出目标，再在总工时内最大化最低检出率，余时允许闲置。"}
  return result
 payload={k:{"N":g["N"],"D":g["D"],"minimum":g["minimum"],"cost_per":stratum_costs[k]} for k,g in strata.items()}
 work=allocate_worktime(payload,total_hours)
 if not work["feasible"]:
  return {"allocation_mode":"worktime","feasible":False,"reason":work["reason"],
   "required_hours":work["required_hours"],"total_hours":total_hours,"target":target,
   "capacity":capacity,"budget":None,"required_budget":None,"strata":ordered,
   "assumption":"工时制：先满足各风险层检出目标，再在总工时内最大化最低检出率，余时允许闲置。"}
 for key,group in strata.items():
  group["cost_per"]=stratum_costs[key]
  group["layer_hours"]=work["quota"][key]*stratum_costs[key]
  group["quota"]=work["quota"][key]
  group["miss_probability"]=miss_probability(group["N"],group["D"],work["quota"][key])
  group["detection_probability"]=1-group["miss_probability"]
  group["guaranteed"]=group["D"]>0 and work["quota"][key]>group["N"]-group["D"]
 total_quota=sum(work["quota"].values())
 result={"allocation_mode":"worktime","feasible":work["feasible"],"reason":work["reason"],
  "required_hours":work["required_hours"],"used_hours":work["used_hours"],
  "idle_hours":work["idle_hours"],"total_hours":total_hours,
  "total_quota":total_quota,"target":target,"capacity":capacity,
  # 兼容旧前端字段：份数口径下的预算/最低需求在工时模式下置空。
  "budget":None,"required_budget":None,"strata":ordered,
  "assumption":"工时制：各层按单份耗时占用总工时，先满足各风险层检出目标的最小样本，再把最低检出率尽量提高；同效取耗时最少的整数配额，余时允许闲置。"}
 return result
