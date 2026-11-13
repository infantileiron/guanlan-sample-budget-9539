<script setup lang="ts">
import {ref,computed,onMounted} from 'vue';
import {useRouter} from 'vue-router';
import {plans} from '../stores/plans';
import {lots} from '../stores/lots';
import {runs} from '../stores/runs';
import {canWrite} from '../stores/auth';
import {useTask} from '../hooks/useTask';
import {pct} from '../utils/format';
import {strata,strataLabels} from '../constants/enums';
import PageHeading from '../components/common/PageHeading.vue';
import Notice from '../components/common/Notice.vue';
const name=ref(''),selected=ref<string[]>([]),target=ref(.95),budget=ref(480),seed=ref(20261112);
const worktimeMode=ref(false);
const totalHours=ref(900);
const costs=ref<Record<string,number>>({low:1,moderate:2,high:3,critical:4});
const {error,busy,act}=useTask();
const router=useRouter();
onMounted(async()=>{await Promise.all([plans.load(),lots.load()]);selected.value=lots.items.value.filter(r=>r.id.startsWith('demo-')).map(r=>r.id)});
const selectedStrata=computed(()=>[...new Set(lots.items.value.filter(r=>selected.value.includes(r.id)).map(r=>r.stratum))].sort());
function submit(){
 act(async()=>{
  const payload:Record<string,unknown>={name:name.value,lot_ids:selected.value,target_detection:target.value,budget:budget.value,seed:seed.value};
  if(worktimeMode.value){
   payload.total_hours=totalHours.value;
   payload.stratum_costs=Object.fromEntries(strata.map(s=>[s,costs.value[s]??1]));
  }
  await plans.create(payload);name.value='';
 });
}
function execute(id:string){act(async()=>{const r=await runs.create({plan_id:id});await router.push('/allocation?run='+r.id)})}
</script><template><PageHeading index="02 / 抽样计划" title="先定检出目标，再看工时够不够。" note="目标按风险层判断。工时制按各层单份耗时占用总工时，先满足各层目标，再尽量抬高最低检出率；旧份数计划仍按份数预算。"/><Notice :message="error"/><div class="two-col"><section><article v-for="r in plans.items.value" :key="r.id" class="plan-row"><p class="eyebrow">SAMPLING PLAN</p><h2>{{r.name}}</h2><dl><div><dt>层级目标</dt><dd>{{pct(r.target_detection)}}</dd></div><div v-if="r.total_hours"><dt>总工时</dt><dd>{{r.total_hours}}</dd></div><div v-else><dt>总预算(份)</dt><dd>{{r.budget}}</dd></div><div><dt>选择批次</dt><dd>{{r.lot_ids.length}}</dd></div></dl><p class="seed-note">seed {{r.seed}} · {{r.total_hours?'工时制 · 余时可闲置':'份数预算'}} · 无放回抽样</p><button v-if="canWrite()" :disabled="busy" @click="execute(r.id)">计算预算与样本 →</button></article></section><form v-if="canWrite()" class="editor-panel" @submit.prevent="submit"><h2>建立抽样计划</h2><label>计划名称<input v-model="name" required minlength="2"></label><fieldset><legend>纳入批次</legend><label v-for="r in lots.items.value" :key="r.id" class="checkbox-label"><input type="checkbox" :value="r.id" v-model="selected">{{r.name}} <small>{{r.size}}份</small></label></fieldset><label class="checkbox-label" style="font-size:11px"><input type="checkbox" v-model="worktimeMode" style="width:13px;height:13px">启用工时制（按各层单份耗时与总工时分配）</label><div v-if="worktimeMode" class="worktime-box"><label>总复核工时<input type="number" v-model.number="totalHours" min="1" max="10000000"></label><p class="eyebrow">各风险层单份耗时</p><div v-for="s in strata" :key="s" class="cost-row"><span>{{strataLabels[s]}}</span><input type="number" v-model.number="costs[s]" min="1" max="1000"><small v-if="!selectedStrata.includes(s)">本计划未选该层</small></div></div><div class="form-pair"><label>目标检出率<input type="number" v-model.number="target" min="0" max="1" step=".01"></label><label v-if="!worktimeMode">总复核预算(份)<input type="number" v-model.number="budget" min="1" max="5000"></label></div><label>随机种子<input type="number" v-model.number="seed" min="0" max="2147483647"></label><button :disabled="busy||!selected.length">保存计划口径</button></form></div></template>
