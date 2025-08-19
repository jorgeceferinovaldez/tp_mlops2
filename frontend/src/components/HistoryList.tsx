import { Stack, Typography, useTheme } from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PredictionBadge from "./PredictionBadge";
import type { HistoryItem } from "../types";

export default function HistoryList({ items }: { items: HistoryItem[] }) {
  const theme = useTheme();

  if (!items.length) {
    return (
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={1}
        sx={{
          width: "100%",
          height: 160,
          padding: 2,
          border: `1px dashed ${theme.palette.divider}`,
          borderRadius: 2,
          backgroundColor: "#1a1f2c",
        }}
      >
        <SmartToyIcon sx={{ fontSize: 50, color: theme.palette.text.secondary }} />
        <Typography
          variant="h6"
          color={theme.palette.text.secondary}
          fontStyle="italic"
          fontFamily="Michroma, monospace"
          sx={{ padding: 2 }
          }
        >
          No predictions yet. Run a model to start tracking history.
        </Typography>
      </Stack>
    );
  }

  return (
    <Stack
      spacing={1}
      sx={{
        width: "100%",
        maxHeight: 340,
        overflowY: "auto",
      }}
    >
      {items.map((h, idx) => (
        <Stack
          key={idx}
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 2,
            px: 1.5,
            py: 1,
            backgroundColor: "rgba(255, 255, 255, 0.04)",
          }}
        >
          <Typography variant="caption" color={theme.palette.text.secondary}>
            {h.t}
          </Typography>
          <PredictionBadge label={h.str_output} />
        </Stack>
      ))}
    </Stack>
  );
}
