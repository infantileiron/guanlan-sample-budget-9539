export type Role="admin"|"analyst"|"viewer";
export interface User{email:string;role:Role}
export interface Entity{id:string;created_at:string;[key:string]:any}
export interface Layer{
 stratum:string;N:number;D:number;estimated_rate:number;minimum:number|null;weight:number;
 quota?:number;detection_probability?:number;miss_probability?:number;guaranteed?:boolean;
 cost_per?:number;layer_hours?:number;
}
export interface AllocationResult{
 allocation_mode:"count"|"worktime";feasible:boolean;reason:string;target:number;capacity:number;
 budget:number|null;required_budget:number|null;
 total_hours?:number|null;required_hours?:number|null;used_hours?:number|null;idle_hours?:number|null;
 total_quota?:number;strata:Layer[];assumption:string;seed?:number;
}
export interface DocumentRow{position:number;document_id:string;lot_id:string;lot_name:string;stratum:string}
