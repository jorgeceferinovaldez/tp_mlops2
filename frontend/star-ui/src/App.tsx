import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  AppBar, Box, Button, Card, CardContent, CardHeader,
  Container, Divider, Grid, Stack, Toolbar, Typography
} from "@mui/material";
import ModeTabs from "./components/ModelTabs";
import PredictionBadge from "./components/PredictionBadge";
import InputForm from "./components/InputForm";
import HistoryList from "./components/HistoryList";
import ClassDistribution from "./components/ClassDistribution";
import Timeline from "./components/Timeline";
import ServiceInfo from "./components/ServiceInfo";
import { DEFAULT_SAMPLE, API_BASE } from "./constants";
import type { HistoryItem, Mode, ModelInput, Prediction } from "./types";
import { gqlPredict, kafkaTest, restPredict, servicesInfo } from "./api/api";

export default function App() {
  const [form, setForm] = useState<ModelInput>(DEFAULT_SAMPLE);
  const set = (k:string, v:string) => setForm(f=>({ ...f, [k]: v==="" ? ("" as any) : Number(v) }));
  const reset = () => setForm(DEFAULT_SAMPLE);

  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState<Mode>("REST");
  const [lastResult, setLastResult] = useState<Prediction|null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [server, setServer] = useState<any>(null);
  const [error, setError] = useState<string|null>(null);

  const classCounts = useMemo(()=>{
    const m: Record<string, number> = { Galaxy:0, OSO:0, Star:0 };
    for (const r of history) if (r.str_output in m) m[r.str_output] += 1;
    return Object.entries(m).map(([name, count])=>({ name, count }));
  },[history]);

  const timeline = useMemo(()=>[...history].reverse().map((d,i)=>({ idx:i+1, code:d.int_output })),[history]);

  async function onPredict() {
    setBusy(true); setError(null);
    try {
      if (mode === "REST") {
        const data = await restPredict(form);
        setLastResult(data);
        setHistory(h=>[{ t:new Date().toLocaleTimeString(), ...data }, ...h].slice(0,50));
      } else if (mode === "GraphQL") {
        const data = await gqlPredict(form);
        setLastResult(data);
        setHistory(h=>[{ t:new Date().toLocaleTimeString(), ...data }, ...h].slice(0,50));
      } else {
        await kafkaTest(form);
        const sent = { int_output: NaN as any, str_output: "Sent to Kafka" };
        setLastResult(sent);
        setHistory(h=>[{ t:new Date().toLocaleTimeString(), ...sent }, ...h].slice(0,50));
      }
    } catch (e:any) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  async function detect() {
    setError(null);
    try {
      const info = await servicesInfo();
      setServer(info.services);
    } catch (e:any) {
      setError(e.message || String(e));
    }
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#0b1020" }}>
      <AppBar position="sticky" color="transparent" elevation={0}
              sx={{ borderBottom: "1px solid #1f2937", backdropFilter: "blur(8px)" }}>
        <Toolbar>
          <Container maxWidth="lg" sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <Typography variant="h6">Star Classifier — UI</Typography>
            <Stack direction="row" spacing={2} alignItems="center">
              <ModeTabs mode={mode} onChange={setMode}/>
              <Button variant="outlined" onClick={detect}>Detect Services</Button>
            </Stack>
          </Container>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {/* Left column */}
          <Grid item xs={12} lg={8}>
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              <InputForm
                form={form} set={set} onSubmit={onPredict}
                busy={busy} ctaLabel={mode==="Kafka" ? "Send to Kafka" : "Predict"} onReset={reset}
              />

              {error && (
                <Box mt={2}>
                  <Card sx={{ bgcolor: "#0b1324", border: "1px solid #1f2937" }}>
                    <CardContent>
                      <Typography color="error">{error}</Typography>
                    </CardContent>
                  </Card>
                </Box>
              )}

              <Grid container spacing={2} mt={1}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ bgcolor: "#0b1324" }}>
                    <CardHeader title={<Typography variant="subtitle1">Last Result</Typography>} />
                    <CardContent>
                      {lastResult ? (
                        <Stack direction="row" spacing={2} alignItems="center">
                          <PredictionBadge label={lastResult.str_output}/>
                          <Typography variant="body2" color="#94a3b8">
                            code: {String(lastResult.int_output)}
                          </Typography>
                        </Stack>
                      ) : (
                        <Typography variant="body2" color="#94a3b8">No results yet.</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ bgcolor: "#0b1324" }}>
                    <CardHeader title={<Typography variant="subtitle1">Class Distribution (this session)</Typography>} />
                    <CardContent>
                      <ClassDistribution data={classCounts}/>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </motion.div>
          </Grid>

          {/* Right column */}
          <Grid item xs={12} lg={4}>
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              <Stack spacing={3}>
                <Card sx={{ bgcolor: "#0f172a", border: "1px solid #1f2937" }}>
                  <CardHeader title={<Typography variant="h6">Prediction History</Typography>} />
                  <CardContent>
                    <HistoryList items={history}/>
                    <Divider sx={{ my: 2 }}/>
                    <Typography variant="subtitle1">Session Timeline</Typography>
                    <Timeline data={timeline}/>
                  </CardContent>
                </Card>

                <ServiceInfo services={server}/>
              </Stack>
            </motion.div>
          </Grid>
        </Grid>
      </Container>

      <Box textAlign="center" py={3} sx={{ color: "#94a3b8" }}>
        API base: {API_BASE || "(same origin)"} · Switch protocol with the top tabs (REST / GraphQL / Kafka test)
      </Box>
    </Box>
  );
}
