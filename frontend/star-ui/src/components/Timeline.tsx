import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Line
} from "recharts";

export default function Timeline({ data }:{
  data:{ idx:number; code:number }[]
}) {
  return (
    <div style={{ width: "100%", height: 200 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="idx" />
          <YAxis allowDecimals={false} domain={[0,2]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="code" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
