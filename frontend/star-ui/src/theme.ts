// src/theme.ts
import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: "#0b1020", paper: "#0f172a" },
    text: { primary: "#ffffff", secondary: "#e2e8f0" },
  },
  components: {
    MuiTypography: {
      styleOverrides: {
        root: {
          color: "#ffffff", // ← tipografía en blanco por defecto
        },
      },
    },
  },
});

export default theme;
