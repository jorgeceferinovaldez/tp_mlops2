import { createTheme } from "@mui/material/styles";

export const galaxyTheme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: "#0b1020",
      paper: "#0f172a",
    },
    primary: {
      main: "#00ffff", // cian brillante
    },
    text: {
      primary: "#e0f7ff",
      secondary: "#94a3b8",
    },
  },
  typography: {
    fontFamily: "'Orbitron', 'Michroma', sans-serif",
  },
  shape: {
    borderRadius: 12,
  },
});
