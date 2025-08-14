import React from "react";
import { Chip } from "@mui/material";
import { CLASS_COLORS } from "../constants";

export default function PredictionBadge({ label }:{ label:string }) {
  return <Chip label={label} sx={{ bgcolor: CLASS_COLORS[label] || "#90a4ae", color: "#0b1020", fontWeight: 600 }} />;
}
