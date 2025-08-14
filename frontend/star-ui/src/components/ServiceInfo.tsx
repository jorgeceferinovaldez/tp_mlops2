import React from "react";
import { Box, Card, CardContent, CardHeader, Typography } from "@mui/material";

export default function ServiceInfo({ services }:{ services:any }) {
  return (
    <Card sx={{ bgcolor: "#0f172a", color: 'white', border: "1px solid #1f2937" }}>
      <CardHeader title={<Typography variant="h6">Detected Services</Typography>} />
      <CardContent>
        {services
          ? <Box component="pre" sx={{ color: "#e2e8f0", whiteSpace: "pre-wrap", fontSize: 12 }}>
              {JSON.stringify(services, null, 2)}
            </Box>
          : <Typography variant="body2" color="white">
              Click "Detect Services" for /services response.
            </Typography>
        }
      </CardContent>
    </Card>
  );
}
