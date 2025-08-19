import { API_BASE } from "../constants";
import type { ModelInput, Prediction } from "../types";

const GQL_MUT = `mutation Predict($features: StarClassificationInput!) {
  predict(features: $features) { intOutput strOutput }
}`;

export async function restPredict(payload: ModelInput): Promise<Prediction> {
  const res = await fetch(`${API_BASE}/predict/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ features: payload }),
  });
  if (!res.ok) throw new Error(`REST ${res.status}`);
  return res.json();
}

export async function gqlPredict(payload: ModelInput): Promise<Prediction> {
  const vars = {
    features: {
      objID: payload.obj_ID, alpha: payload.alpha, delta: payload.delta,
      u: payload.u, g: payload.g, r: payload.r, i: payload.i, z: payload.z,
      runID: payload.run_ID, camCol: payload.cam_col, fieldID: payload.field_ID,
      specObjID: payload.spec_obj_ID, redshift: payload.redshift,
      plate: payload.plate, MJD: payload.MJD, fiberID: payload.fiber_ID,
    },
  };
  const res = await fetch(`${API_BASE}/graphql`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: GQL_MUT, variables: vars }),
  });
  if (!res.ok) throw new Error(`GraphQL ${res.status}`);
  const g = await res.json();
  if (g.errors) throw new Error(g.errors?.[0]?.message || "GraphQL error");
  return { int_output: g.data.predict.intOutput, str_output: g.data.predict.strOutput };
}

export async function kafkaTest(payload: ModelInput) {
  const res = await fetch(`${API_BASE}/stream/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Kafka test ${res.status}`);
  return res.json();
}

export async function servicesInfo() {
  const res = await fetch(`${API_BASE}/services`);
  if (!res.ok) throw new Error(`Services ${res.status}`);
  return res.json();
}
