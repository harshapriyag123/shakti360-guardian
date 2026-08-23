import { useState } from "react";
import { SafeAreaView, ScrollView, Text, Pressable, View } from "react-native";
import { post } from "../lib/api";

export default function Privacy() {
  const [result, setResult] = useState<any>(null);

  async function check() {
    setResult(await post("/agents/privacy", {
      active_journey: false,
      location_permission: "always",
      notification_preview_enabled: true,
      evidence_encrypted: true,
      app_lock_enabled: false
    }));
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
        <Text style={{ fontSize: 26, fontWeight: "800" }}>Privacy Guardian</Text>
        <Pressable onPress={check} style={{ padding: 16, borderWidth: 1, borderRadius: 12 }}>
          <Text style={{ fontWeight: "800" }}>Run privacy check</Text>
        </Pressable>
        {result && (
          <View style={{ padding: 14, borderWidth: 1, borderRadius: 12, gap: 6 }}>
            <Text style={{ fontSize: 22, fontWeight: "800" }}>
              Privacy score: {result.privacy_score}/100
            </Text>
            {result.issues.map((i:string) => <Text key={i}>• {i}</Text>)}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
