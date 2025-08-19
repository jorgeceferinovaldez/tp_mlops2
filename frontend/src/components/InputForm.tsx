import { Button, Card, CardContent, Grid, Typography, Box } from "@mui/material";
import FeatureField from "./FeatureField";
import type { ModelInput } from "../types";

export default function InputForm({
  form, set, onSubmit, busy, ctaLabel, onReset
}: {
  form: ModelInput; set: (k: string, v: string) => void; onSubmit: () => void;
  busy: boolean; ctaLabel: string; onReset: () => void;
}) {
  return (
    <Card
      sx={{
        bgcolor: "#0f172a",
        border: "2px solid #00ffff55",
        boxShadow: "0 0 12px #00ffff44",
        borderRadius: "16px",
        p: 2,
      }}
    >
      <Typography
        variant="h5"
        sx={{
          color: "#00ffff",
          fontFamily: "'Michroma', sans-serif",
          mb: 2,
        }}
      >
        Input Features
      </Typography>

      <CardContent sx={{ p: 0 }}>
        <Grid container spacing={2}>
          {Object.entries(form).map(([k, v]) => (
            <Grid key={k} item xs={12} sm={6}>
              <FeatureField name={k} value={v as number} onChange={set} />
            </Grid>
          ))}
        </Grid>

        <Box
          mt={3}
          sx={{
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Button
            onClick={onReset}
            sx={{
              color: "#fff",
              border: "1px solid #94a3b8",
              borderRadius: "12px",
              px: 3,
              py: 1,
              "&:hover": {
                backgroundColor: "#1e293b",
              },
            }}
          >
            Reset
          </Button>

          <Button
            variant="outlined"
            onClick={onSubmit}
            disabled={busy}
            sx={{
              color: "#00ffff",
              border: "2px solid #00ffff",
              borderRadius: "12px",
              px: 4,
              py: 1.5,
              fontWeight: "bold",
              boxShadow: "0 0 8px #00ffff66",
              "&:hover": {
                backgroundColor: "#00ffff22",
              },
            }}
          >
            {busy ? "Working…" : ctaLabel}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}
