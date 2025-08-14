import React from "react";
import { Button, Card, CardContent, CardHeader, Grid, Typography } from "@mui/material";
import FeatureField from "./FeatureField";
import type { ModelInput } from "../types";

export default function InputForm({
  form, set, onSubmit, busy, ctaLabel, onReset
}:{
  form: ModelInput; set:(k:string,v:string)=>void; onSubmit:()=>void;
  busy:boolean; ctaLabel:string; onReset:()=>void;
}) {
  return (
    <Card sx={{ bgcolor: "#0f172a", border: "1px solid #1f2937" }}>
      <CardHeader
        title={<Typography variant="h6" sx={{color: 'white'}}>Input Features</Typography>}
        action={
          <>
            <Button onClick={onReset}>Reset</Button>
            <Button variant="contained" onClick={onSubmit} disabled={busy}>
              {busy ? "Working…" : ctaLabel}
            </Button>
          </>
        }
      />
      <CardContent>
        <Grid container spacing={2}>
          {Object.entries(form).map(([k,v])=> (
            <Grid key={k} item xs={12} sm={6} md={4}>
              <FeatureField name={k} value={v as number} onChange={set}/>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
}
