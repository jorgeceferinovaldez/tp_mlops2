import React from "react";
import { Tabs, Tab } from "@mui/material";
import type { Mode } from "../types";

export default function ModeTabs({ mode, onChange }:{ mode: Mode; onChange:(m:Mode)=>void }) {
  const value = ["REST","GraphQL","Kafka"].indexOf(mode);
  return (
    <Tabs value={value} onChange={(_, idx)=>onChange(["REST","GraphQL","Kafka"][idx] as Mode)}>
      <Tab label="REST"/>
      <Tab label="GraphQL"/>
      <Tab label="Kafka"/>
    </Tabs>
  );
}
