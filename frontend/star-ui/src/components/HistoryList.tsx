import React from "react";
import { Stack, Typography } from "@mui/material";
import PredictionBadge from "./PredictionBadge";
import type { HistoryItem } from "../types";

export default function HistoryList({ items }:{ items: HistoryItem[] }) {
  if (!items.length) {
    return <Typography variant="body2" color="#ffff">Run a prediction to populate history.</Typography>;
  }
  return (
    <Stack spacing={1} sx={{ maxHeight: 340, overflow: "auto" }}>
      {items.map((h, idx)=> (
        <Stack
          key={idx}
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ border: "1px solid #1f2937", borderRadius: 2, px: 1.5, py: 1 }}
        >
          <Typography variant="caption" color="#94a3b8">{h.t}</Typography>
          <PredictionBadge label={h.str_output}/>
        </Stack>
      ))}
    </Stack>
  );
}
