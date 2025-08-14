import { blue, deepPurple, orange } from "@mui/material/colors";
import type { ModelInput } from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const API_BASE = (import.meta as any).env?.VITE_API_BASE || "";

export const CLASS_COLORS: Record<string, string> = {
  Galaxy: deepPurple[300],
  OSO: blue[300],
  Star: orange[400],
};

export const DEFAULT_SAMPLE: ModelInput = {
  obj_ID: 123456789.0,
  alpha: 180.0,
  delta: 45.0,
  u: 22.4,
  g: 21.6,
  r: 21.1,
  i: 20.9,
  z: 20.7,
  run_ID: 756,
  cam_col: 3,
  field_ID: 674,
  spec_obj_ID: 567890123.0,
  redshift: 0.123,
  plate: 2345,
  MJD: 58583,
  fiber_ID: 456,
};
