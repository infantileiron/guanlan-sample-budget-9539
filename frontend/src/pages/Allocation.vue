<script setup lang="ts">
import {ref,computed,onMounted,onUnmounted,watch} from 'vue';
import {useRoute} from 'vue-router';
import {runs} from '../stores/runs';
import {draws} from '../stores/draws';
import PageHeading from '../components/common/PageHeading.vue';
import StatusPill from '../components/common/StatusPill.vue';
import Notice from '../components/common/Notice.vue';
import EmptyState from '../components/common/EmptyState.vue';
import AllocationTable from '../components/AllocationTable.vue';
import QuotaBars from '../components/QuotaBars.vue';
const route=useRoute(),selected=ref(String(route.query.run||'demo-run'));
watch(()=>route.query.run,value=>{selected.value=String(value||'demo-run')});
let timer:ReturnType<typeof setInterval>;
onMounted(()=>{runs.load();draws.load();timer=setInterval(()=>{runs.load();draws.load()},2000)});
onUnmounted(()=>clearInterval(timer));
const run=computed(()=>runs.items.value.find(r=>r.id===selected.value));
const result=computed(()=>run.value?.result);
const isWorktime=computed(()=>result.value?.allocation_mode==='worktime');
const draw=computed(()=>draws.items.value.find(r=>r.run_id===selected.value));
</script><template><PageHeading index="03 / 预算分层" title="每一份配额，都能还原到假设。" :note="isWorktime?'工时制按各层单份耗时占用总工时：先满足各层检出目标，再抬高最低检出率，余时允许闲置；工时不够不会生成抽样。':'超几何模型精确计算无放回漏检率；整数配额满足最低需求、层容量与总预算。预算不够不会生成抽样。'"/><div class="result-toolbar"><label>运行记录<select v-model="selected"><option v-for="r in runs.items.value" :key="r.id" :value="r.id">{{r.id==='demo-run'?'四层基线':r.id==='demo-worktime-run'?'工时制基线':r.id.slice(0,8)}} · {{r.status}}</option></select></label><StatusPill v-if="run" :status="run.status"/></div><Notice :message="runs.error.value"/><Notice v-if="run?.status==='failed'" :message="run.error"/><EmptyState v-if="run&&['queued','running'].includes(run.status)" text="后台正在求最小样本量、整数配额和具体文档样本，每两秒刷新。"/><div v-if="result&&['completed','infeasible'].includes(run?.status||'')" class="allocation-layout"><section><div v-if="isWorktime" class="budget-line"><div><small>总工时</small><strong>{{result.total_hours}}</strong></div><div><small>最低工时</small><strong>{{result.required_hours??'不可达'}}</strong></div><div><small>已用工时</small><strong>{{result.used_hours??'—'}}</strong></div><div><small>剩余工时</small><strong>{{result.idle_hours??'—'}}</strong></div><div><small>清单份数</small><strong>{{result.total_quota??'—'}}</strong></div></div><div v-else class="budget-line"><div><small>给定预算</small><strong>{{result.budget}}</strong></div><div><small>最低需求</small><strong>{{result.required_budget??'不可达'}}</strong></div><div><small>总体容量</small><strong>{{result.capacity}}</strong></div></div><Notice v-if="!result.feasible" :message="result.reason"/><AllocationTable :rows="result.strata" :mode="isWorktime?'worktime':'count'"/><p class="method-note">{{result.assumption}}</p><router-link v-if="draw" :to="'/draws?draw='+draw.id" class="action-link">打开 {{draw.manifest.length}} 份具体文档清单 →</router-link><p v-if="result.feasible&&!draw" class="method-note">配额已完成，正在保存抽样清单…</p><p v-if="isWorktime&&result.feasible" class="method-note">逐层用时合计 {{result.used_hours}} 工时，剩余 {{result.idle_hours}} 工时允许闲置。</p></section><aside class="margin-note"><p class="eyebrow">ALLOCATION BASIS</p><h2>配额如何分配</h2><QuotaBars :rows="result.strata"/><p v-if="isWorktime">各层按单份耗时计费。先保证每层达到检出目标的最小样本，再把剩余工时投向当前检出率最低的层，直到买不起下一份；同效取耗时最少的整数配额。seed={{result.seed}}。</p><p v-else>权重=N×√(p×(1−p))，p为层内按文档量加权预估差错率。带最低样本与容量约束求连续配额，再按最大余数整数化。</p><p v-if="!isWorktime">正方差层满额后仍有预算，零方差层按固定顺序分配剩余额度。seed={{result.seed}}。</p></aside></div></template>
