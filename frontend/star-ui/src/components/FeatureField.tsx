import React from "react";
import { TextField } from "@mui/material";

export default function FeatureField({ name, value, onChange }:{
  name:string; value:number; onChange:(k:string,v:string)=>void
}) {
  return (
    <TextField
      size="small"
      label={name}
      type="number"
      value={value}
      onChange={(e)=>onChange(name, e.target.value)}
      fullWidth
    />
  );
}
