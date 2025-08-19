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
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/material";

export default function Timeline({ data }: { data: { idx: number; code: number }[] }) {
  const theme = useTheme();

  return (
    <Box style={{ width: "100%", height: 200 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            dataKey="idx"
            tick={{ fill: theme.palette.text.secondary }}
            label={{ value: "Index", position: "insideBottom", fill: theme.palette.text.primary }}
          />
          <YAxis
            allowDecimals={false}
            domain={[0, 2]}
            tick={{ fill: theme.palette.text.secondary }}
          />
          <Tooltip
            contentStyle={{
              background: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              color: theme.palette.text.primary,
            }}
            labelStyle={{ color: theme.palette.text.primary }}
            itemStyle={{ color: theme.palette.text.primary }}
          />
          <Legend
            wrapperStyle={{ color: theme.palette.text.secondary }}
            iconType="circle"
          />
          <Line
            type="monotone"
            dataKey="code"
            stroke="#00ffff"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            name="Code"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}
