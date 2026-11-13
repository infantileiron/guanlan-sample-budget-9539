"""工时制整数配额：先满足各风险层检出目标，再字典序最大化最低检出率。

约束为总工时 H 与各层单份耗时 c_h：sum(c_h n_h) <= H，配额为整数。
- 基线是各层满足检出目标的精确最小样本 L_h；基线工时之和超过 H 即不可行。
- 可行后在剩余工时内逐轮求所有未固定层都能负担的最小漏检阈值（lexicographic
  max-min），买不起公共阈值时逐一固定一层后递归择优；同效取耗时最少的整数配额。
- D=0 层加样无增益，固定在最低样本；余时允许闲置，不把工时浪费在无增益的增量上。
漏检率全程用整数组合数交叉相乘比较，不转浮点；每层漏检序列用相邻组合数递推构造。
"""
import math
from fractions import Fraction


def _leq(a, b):
 return a[0]*b[1] <= b[0]*a[1]


def allocate_worktime(strata, total_hours):
 """strata: {key: {N,D,minimum,cost_per}}；minimum 为 None 表示该层目标不可达。"""
 keys=sorted(strata)
 base_quota={k:strata[k]["minimum"] for k in keys}
 impossible=[k for k in keys if strata[k]["minimum"] is None]
 required_hours=None if impossible else sum(base_quota[k]*strata[k]["cost_per"] for k in keys)
 if impossible:
  reason="假设差错数D=0，非零检出目标不可达："+", ".join(impossible)
 elif required_hours>total_hours:
  reason="总工时低于各风险层目标检出率所需最小工时之和"
 else:
  reason=""
 result={"feasible":not bool(reason),"reason":reason,"required_hours":required_hours,
  "total_hours":total_hours,"quota":dict(base_quota),"used_hours":None,"idle_hours":None,"miss":{}}
 if reason:return result

 def cap(k):
  g=strata[k]
  return g["minimum"] if g["D"]==0 else g["N"]-g["D"]+1

 # 漏检序列缓存：miss_seq[k][n] 为配额 n 的漏检分数 (num,den)，相邻组合数整数递推。
 miss_seq={}
 for k in keys:
  g=strata[k];N,D,c=g["N"],g["D"],cap(k)
  if D==0:
   miss_seq[k]=[(1,1)]*(c+1);continue
  num=[0]*(c+1);den=[0]*(c+1);num[0]=den[0]=1;a=N-D;z=min(c,a)
  for n in range(1,z+1):
   num[n]=num[n-1]*(a-n+1);den[n]=den[n-1]*(N-n+1)
  for n in range(z+1,c+1):
   num[n]=0;den[n]=den[n-1]*(N-n+1)
  miss_seq[k]=list(zip(num,den))

 def miss_at(k,n):return miss_seq[k][n]

 def steps_to(k,q,quota):
  seq=miss_seq[k];lo,hi=0,cap(k)-quota
  while lo<hi:
   mid=(lo+hi)//2
   if _leq(seq[quota+mid],q):hi=mid
   else:lo=mid+1
  return lo

 def detection_key(quota):
  return tuple(sorted((Fraction(*miss_at(k,quota[k])) for k in keys),reverse=True))

 def solve(fixed,quota,remaining):
  moving=[k for k in keys if k not in fixed and quota[k]<cap(k)]
  if not moving or remaining<min(strata[k]["cost_per"] for k in moving):return quota
  best_q=None
  for pivot in moving:
   seq=miss_seq[pivot];first_q=seq[quota[pivot]+1]
   if sum(strata[k]["cost_per"]*steps_to(k,first_q,quota[k]) for k in moving)>remaining:continue
   lo,hi=quota[pivot]+1,cap(pivot)
   while lo<hi:
    mid=(lo+hi+1)//2;q=seq[mid]
    need=sum(strata[k]["cost_per"]*steps_to(k,q,quota[k]) for k in moving)
    if need<=remaining:lo=mid
    else:hi=mid-1
   pivot_best=seq[lo]
   if best_q is None or _leq(pivot_best,best_q):best_q=pivot_best
  if best_q is not None:
   quota=dict(quota);spent=0
   for k in moving:
    inc=steps_to(k,best_q,quota[k]);quota[k]+=inc;spent+=inc*strata[k]["cost_per"]
   next_fixed=set(fixed)|{k for k in moving if quota[k]>=cap(k)}
   return solve(next_fixed,quota,remaining-spent)
  best=None
  for frozen in moving:
   cand=solve(set(fixed)|{frozen},dict(quota),remaining)
   used=sum(cand[k]*strata[k]["cost_per"] for k in keys)
   score=(detection_key(cand),used,sum(cand.values()),tuple(cand[k] for k in keys))
   if best is None or score<best[0]:best=(score,cand)
  return best[1]

 initial_fixed={k for k in keys if strata[k]["D"]==0 or base_quota[k]>=cap(k)}
 final_quota=solve(initial_fixed,dict(base_quota),total_hours-required_hours)
 used=sum(final_quota[k]*strata[k]["cost_per"] for k in keys)
 result.update(quota=final_quota,used_hours=used,idle_hours=total_hours-used,
  miss={k:miss_at(k,final_quota[k]) for k in keys})
 return result


def miss_probability(N,D,n):
 if n>N-D:return 0.
 return math.comb(N-D,n)/math.comb(N,n)
