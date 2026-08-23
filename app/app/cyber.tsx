import { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { post } from "../lib/api";
import { Action, Card, colors, ErrorBanner, Eyebrow, Field, Loading, Pill, Screen, Title } from "../lib/ui";

type Scan = { risk_level: string; risk_score: number; signals: Array<{ signal: string; explanation?: string } | string>; disclaimer: string };
const examples = ["URGENT: send gift cards now and click http://bit.ly/demo", "Hi, your parcel arrives tomorrow between 2–4pm."];
export default function Cyber() {
  const [text, setText] = useState(examples[0]); const [result, setResult] = useState<Scan | null>(null); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function analyze() { try { setBusy(true); setError(""); setResult(await post<Scan>("/agents/cyber", { text })); } catch (e) { setError(e instanceof Error ? e.message : "Scan failed"); } finally { setBusy(false); } }
  const tone = result?.risk_level === "high" ? "red" : result?.risk_level === "medium" ? "gold" : "green";
  return <Screen><Eyebrow>CYBER GUARDIAN</Eyebrow><Title subtitle="Paste a suspicious SMS, email, or chat. Nothing is inferred about the sender.">Check before you click</Title>
    <Card><Field label="Message to analyze" multiline value={text} onChangeText={setText} placeholder="Paste the message here…" /><View style={{ flexDirection: "row", gap: 8 }}><Pressable onPress={() => { setText(examples[0]); setResult(null); }}><Text style={{ color: colors.primary, fontWeight: "800" }}>Use scam example</Text></Pressable><Text style={{ color: colors.border }}>|</Text><Pressable onPress={() => { setText(examples[1]); setResult(null); }}><Text style={{ color: colors.primary, fontWeight: "800" }}>Use safe example</Text></Pressable></View><Action label="Analyze message" icon="scan" onPress={analyze} disabled={busy || !text.trim()} /></Card>
    {busy ? <Loading label="Checking language, links, and pressure tactics…" /> : null}{error ? <ErrorBanner message={error} retry={analyze} /> : null}
    {result ? <Card tone={tone === "red" ? "danger" : tone === "green" ? "mint" : "plain"}><View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}><View><Text style={{ color: colors.muted, fontWeight: "700" }}>RISK SCORE</Text><Text style={{ color: colors.ink, fontSize: 38, fontWeight: "900" }}>{result.risk_score}<Text style={{ fontSize: 18 }}>/100</Text></Text></View><Pill label={`${result.risk_level} risk`} tone={tone} /></View><Text style={{ color: colors.ink, fontSize: 18, fontWeight: "900" }}>{tone === "red" ? "Pause. Don’t click or send money." : tone === "gold" ? "Verify through another channel." : "No common scam signals found."}</Text><View style={{ gap: 9 }}>{result.signals.map((item, i) => { const label = typeof item === "string" ? item : item.signal; return <View key={`${label}-${i}`} style={{ flexDirection: "row", gap: 9 }}><Text style={{ color: colors.coral }}>●</Text><Text style={{ color: colors.ink, flex: 1, lineHeight: 20 }}>{label.replaceAll("_", " ")}</Text></View>; })}</View><Text style={{ color: colors.muted, fontSize: 12, lineHeight: 17 }}>{result.disclaimer}</Text></Card> : null}
  </Screen>;
}
