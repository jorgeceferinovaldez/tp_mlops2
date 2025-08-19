import { Chip } from "@mui/material";
import { CLASS_COLORS } from "../constants";

export default function PredictionBadge({ label }: { label: string }) {
  const baseColor = CLASS_COLORS[label] || "#90a4ae";

  return (
    <Chip
      label={label}
      sx={{
        width: '100%',
        bgcolor: baseColor,
        color: "#0b1020",
        fontFamily: "Michroma, sans-serif",
        fontWeight: 600,
        maxWidth: 300,
        borderRadius: "9999px",
        px: 1.5,
        boxShadow: `0 0 10px ${baseColor}55`,
        "& .MuiChip-label": {
          fontSize: "0.85rem",
        },
      }}
    />
  );
}
