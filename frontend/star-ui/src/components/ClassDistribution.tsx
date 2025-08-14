import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  Cell,
} from "recharts";
import { useTheme } from "@mui/material/styles";
import { CLASS_COLORS } from "../constants";

type Row = { name: string; count: number };

export default function ClassDistribution({ data }: { data: Row[] }) {
  const theme = useTheme();

  return (
    <div style={{ width: "100%", height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="name" tick={{ fill: theme.palette.text.secondary }} />
          <YAxis allowDecimals={false} tick={{ fill: theme.palette.text.secondary }} />
          <Tooltip
            contentStyle={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}` }}
            labelStyle={{ color: theme.palette.text.primary }}
            itemStyle={{ color: theme.palette.text.primary }}
          />
          <Legend wrapperStyle={{ color: theme.palette.text.secondary }} iconType="circle" />
          <Bar dataKey="count" name="Cantidad">
            {data.map((entry, idx) => (
              <Cell
                key={`cell-${idx}`}
                fill={CLASS_COLORS[entry.name] ?? theme.palette.primary.main}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
