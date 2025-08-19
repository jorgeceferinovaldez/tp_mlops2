import { Box, Card, CardContent, CardHeader, Typography } from "@mui/material";

export default function ServiceInfo({ services }: { services: any }) {
  return (
    <Card
      sx={{
        width: '100%',
        bgcolor: "#0f172a",
        color: "white",
        border: "1px solid #1f2937",
        boxShadow: "0 0 10px rgba(0, 255, 255, 0.2)", // efecto glow cian
        borderRadius: 2,
        backdropFilter: "blur(6px)", // capa tipo vidrio
      }}
    >
      <CardHeader
        title={
          <Typography variant="h5" sx={{ color: "#00ffff", fontFamily: "Michroma, sans-serif" }}>
            Detected Services
          </Typography>
        }
      />
      <CardContent>
        {services ? (
          <Box
            component="pre"
            sx={{
              width: '100%',
              color: "#e2e8f0",
              whiteSpace: "pre-wrap",
              fontSize: 12,
              fontFamily: "monospace",
              bgcolor: "#1a1f2c",
              p: 2,
              border: "1px solid #2d3748",
              maxHeight: 300,
              overflowY: "auto",
            }}
          >
            {JSON.stringify(services, null, 2)}
          </Box>
        ) : (
          <Typography variant="body2" color="white" fontStyle="italic">
            Click "Detect Services" to fetch <code>/services</code> response.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
