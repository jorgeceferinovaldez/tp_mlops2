// src/types.ts
export type Mode = "REST" | "GraphQL" | "Kafka";

export type Prediction = { int_output: number; str_output: string };

export type HistoryItem = {
  t: string;
  int_output: number;
  str_output: string;
};

export type ModelInput = {
  obj_ID: number; alpha: number; delta: number;
  u: number; g: number; r: number; i: number; z: number;
  run_ID: number; cam_col: number; field_ID: number;
  spec_obj_ID: number; redshift: number; plate: number; MJD: number; fiber_ID: number;
};
