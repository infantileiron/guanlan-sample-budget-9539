<script setup lang="ts">
import type {Layer} from '../types/domain';
import {strataLabels} from '../constants/enums';
import {detectionPct} from '../utils/format';
const props=defineProps<{rows:Layer[];mode?:'count'|'worktime'}>();
</script><template><div class="table-wrap"><table><thead><tr><th>风险层</th><th>文档 N</th><th>假设 D</th><th>最小样本</th><th>最终配额</th><th>检出率</th><th v-if="props.mode==='worktime'">单份耗时</th><th v-if="props.mode==='worktime'">层用时</th></tr></thead><tbody><tr v-for="r in rows" :key="r.stratum"><td>{{strataLabels[r.stratum]}}</td><td>{{r.N}}</td><td>{{r.D}}</td><td>{{r.minimum===null?'不可达':r.minimum}}</td><td>{{r.quota??'—'}}</td><td>{{r.detection_probability===undefined?'—':detectionPct(r.detection_probability,r.guaranteed)}}</td><td v-if="props.mode==='worktime'">{{r.cost_per??'—'}}</td><td v-if="props.mode==='worktime'">{{r.layer_hours??'—'}}</td></tr></tbody></table></div></template>
