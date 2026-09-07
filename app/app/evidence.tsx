import { useState } from "react";
import { Text } from "react-native";
import { authPost } from "../lib/api";
import { Action, Card, colors, ErrorBanner, Eyebrow, Field, Loading, Screen, Title } from "../lib/ui";

type EvidenceRecord = {
  id: string;
  created_at: string;
  ai_summary: { summary: string };
};

export default function Evidence() {
  const [description, setDescription] = useState("Received repeated unwanted messages after I asked the sender to stop.");
  const [record, setRecord] = useState<EvidenceRecord | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function save() {
    try {
      setBusy(true);
      setError("");
      const data = await authPost<EvidenceRecord>("/incidents", {
        title: "Unwanted contact",
        description: description.trim(),
        occurred_at: new Date().toISOString(),
        tags: ["digital", "unwanted-contact"],
      });
      setRecord(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "The incident could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  return <Screen>
    <Eyebrow>ACCOUNT-PRIVATE RECORD</Eyebrow>
    <Title subtitle="Structure only what you record. Shakti360 does not infer guilt or intent.">Evidence Vault</Title>
    <Card tone="mint">
      <Text style={{ color: colors.primaryDark, fontWeight: "900" }}>Separated by account</Text>
      <Text style={{ color: colors.muted, lineHeight: 20 }}>Sign in before saving. Your records and pattern analysis are no longer shared with other accounts.</Text>
    </Card>
    <Card>
      <Field label="What happened?" multiline value={description} onChangeText={value => { setDescription(value); setRecord(null); }} placeholder="Write only the details you want to record…" />
      <Action label="Save private incident" icon="document-lock" onPress={save} disabled={busy || !description.trim()} />
    </Card>
    {busy ? <Loading label="Structuring your record…" /> : null}
    {error ? <ErrorBanner message={error} /> : null}
    {record ? <Card tone="mint">
      <Text style={{ color: colors.primaryDark, fontWeight: "900", fontSize: 18 }}>Structured summary</Text>
      <Text style={{ color: colors.ink, lineHeight: 21 }}>{record.ai_summary.summary}</Text>
      <Text style={{ color: colors.muted, fontSize: 12 }}>Record {record.id.slice(0, 8).toUpperCase()} • {new Date(record.created_at).toLocaleString()}</Text>
    </Card> : null}
    <Text style={{ color: colors.muted, fontSize: 12, lineHeight: 18 }}>Current hackathon storage is text-only and temporary; do not use it as your only copy of important evidence.</Text>
  </Screen>;
}
