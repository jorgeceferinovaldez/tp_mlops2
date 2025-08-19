import { TextField } from "@mui/material";

export default function FeatureField({
  name,
  value,
  onChange,
}: {
  name: string;
  value: number;
  onChange: (k: string, v: string) => void;
}) {
  return (
    <TextField
      size="small"
      type="number"
      value={value}
      onChange={(e) => onChange(name, e.target.value)}
      fullWidth
      label={name}
      InputLabelProps={{
        style: {
          color: "#00ffff", // color del label
          fontFamily: "Michroma, sans-serif",
        },
      }}
      InputProps={{
        sx: {
          fontFamily: "Michroma, sans-serif",
          color: "#ffffff",
          borderRadius: "12px",
          backgroundColor: "#0f172a",
          border: "1px solid #00ffff55",
          boxShadow: "0 0 6px #00ffff33",
          "&:hover": {
            boxShadow: "0 0 10px #00ffff55",
          },
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#00ffff88",
          },
        },
      }}
      sx={{
        "& .MuiInputBase-root": {
          fontSize: "0.95rem",
        },
      }}
    />
  );
}
