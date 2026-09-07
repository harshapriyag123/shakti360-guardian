import { useState } from "react";
import { Text, View } from "react-native";
import { get } from "../lib/api";
import { Action, Card, colors, ErrorBanner, Eyebrow, Loading, Screen, Title } from "../lib/ui";

type PatternResult = {
  incident_count: number;
  observations: string[];
  disclaimer: string;
};

export default function Patterns() {
  const [result, setResult] = useState<PatternResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    try {
      setBusy(true);
      setError("");
      setResult(await get<PatternResult>("/incidents/patterns"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Pattern analysis could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  return <Screen>
    <Eyebrow>ACCOUNT-PRIVATE INSIGHTS</Eyebrow>
    <Title subtitle="Descriptive analysis across only the incidents recorded by your account.">Pattern intelligence</Title>
    <Card>
      <Text style={{ color: colors.muted, lineHeight: 21 }}>This tool describes repeated details in your records. It does not predict guilt, intent, or danger.</Text>
      <Action label="Analyze my records" icon="analytics" onPress={analyze} disabled={busy} />
    </Card>
    {busy ? <Loading label="Reviewing your saved records…" /> : null}
    {error ? <ErrorBanner message={error} /> : null}
    {result ? <Card tone="mint">
      <Text style={{ color: colors.primaryDark, fontWeight: "900", fontSize: 20 }}>{result.incident_count} {result.incident_count === 1 ? "incident" : "incidents"} reviewed</Text>
      <View style={{ gap: 8 }}>
        {result.observations.length
          ? result.observations.map(observation => <Text key={observation} style={{ color: colors.ink, lineHeight: 20 }}>• {observation}</Text>)
          : <Text style={{ color: colors.muted }}>Not enough repeated signals yet.</Text>}
      </View>
      <Text style={{ color: colors.muted, fontSize: 12, lineHeight: 18 }}>{result.disclaimer}</Text>
    </Card> : null}
  </Screen>;
}
