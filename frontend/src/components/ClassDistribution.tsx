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

type Row = { name: string; count: number };

export default function ClassDistribution({ data }: { data: Row[] }) {
  const theme = useTheme();

  return (
    <div style={{ width: "100%", height: 200 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 16, right: 16, bottom: 0, left: 0 }}
        >
          <defs>
            <linearGradient id="colorGalaxy" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorStar" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f472b6" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ec4899" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorOSO" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#c084fc" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="name"
            tick={{
              fill: "#e2e8f0",
              fontFamily: "Michroma, sans-serif",
              fontSize: 12,
            }}
          />
          <YAxis
            allowDecimals={false}
            tick={{
              fill: "#e2e8f0",
              fontFamily: "Michroma, sans-serif",
              fontSize: 12,
            }}
          />
          <Tooltip
            cursor={{ fill: "#1e293b", opacity: 0.4 }} // ✅ Color espacial suave con opacidad
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              fontFamily: "Michroma, sans-serif",
              color: "#e2e8f0",
              transition: "all 0.3s ease-in-out",
            }}
            labelStyle={{ color: "#f8fafc" }}
            itemStyle={{ color: "#e2e8f0" }}
          />

          <Legend
            wrapperStyle={{
              color: "#94a3b8",
              fontFamily: "Michroma, sans-serif",
              fontSize: 12,
              paddingTop: 8,
            }}
            iconType="circle"
          />
          <Bar
            dataKey="count"
            name="Amount"
            isAnimationActive
            animationDuration={800}
            animationEasing="ease-out"
          >
            {data.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={`url(#color${entry.name})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
