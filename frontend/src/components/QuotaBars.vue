<script setup lang="ts">
import type {Layer} from '../types/domain';
import {strataLabels} from '../constants/enums';
defineProps<{rows:Layer[]}>();
</script><template><div class="quota-bars"><div v-for="r in rows" :key="r.stratum" class="quota-row"><div><strong>{{strataLabels[r.stratum]}}</strong><span>{{r.quota??0}} / {{r.N}}<template v-if="r.layer_hours!==undefined"> · {{r.layer_hours}} 工时</template></span></div><div class="quota-track"><i :style="{width:(r.quota||0)/r.N*100+'%'}"></i><b v-if="r.minimum!==null" :style="{left:r.minimum/r.N*100+'%'}"></b></div><small>竖线为满足目标的最小样本 {{r.minimum??'不可达'}}<template v-if="r.cost_per!==undefined">；单份耗时 {{r.cost_per}}</template></small></div></div></template>
