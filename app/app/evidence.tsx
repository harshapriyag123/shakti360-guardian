import { useState } from "react";
import { SafeAreaView, ScrollView, Text, TextInput, Pressable, View } from "react-native";
import { post } from "../lib/api";

export default function Evidence() {
  const [description, setDescription] = useState("Received repeated unwanted messages after I asked the sender to stop.");
  const [record, setRecord] = useState<any>(null);

  async function save() {
    const data = await post<any>("/incidents", {
      title: "Unwanted contact",
      description,
      occurred_at: new Date().toISOString(),
      tags: ["digital", "unwanted-contact"]
    });
    setRecord(data);
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
        <Text style={{ fontSize: 26, fontWeight: "800" }}>Evidence Vault</Text>
        <Text style={{ opacity: 0.7 }}>
          The AI structures only what the user records; it does not infer guilt or intent.
        </Text>
        <TextInput multiline value={description} onChangeText={setDescription}
          style={{ borderWidth: 1, minHeight: 140, padding: 14, borderRadius: 12 }} />
        <Pressable onPress={save} style={{ padding: 16, borderWidth: 1, borderRadius: 12 }}>
          <Text style={{ fontWeight: "800" }}>Save incident</Text>
        </Pressable>
        {record && (
          <View style={{ borderWidth: 1, borderRadius: 12, padding: 14 }}>
            <Text style={{ fontWeight: "800" }}>Structured summary</Text>
            <Text style={{ marginTop: 8 }}>{record.ai_summary.summary}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
