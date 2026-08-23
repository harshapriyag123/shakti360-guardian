import { useEffect, useState } from "react";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, Text, TextInput, View } from "react-native";
import { readLocal, storageKeys, writeLocal } from "../lib/storage";

export default function QuickExit() {
  const [note, setNote] = useState("");
  const [restored, setRestored] = useState(false);
  useEffect(() => { readLocal<string>(storageKeys.dailyNote).then(value => { if (value) setNote(value); setRestored(true); }); }, []);
  useEffect(() => { if (!restored) return; const timer = setTimeout(() => writeLocal(storageKeys.dailyNote, note), 350); return () => clearTimeout(timer); }, [note, restored]);
  function goBack() {
    if (router.canGoBack()) router.back();
    else router.replace("/");
  }

  return <SafeAreaView style={{ flex: 1, backgroundColor: "#FAFAF8" }}>
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
      <View style={{ flex: 1, padding: 24, gap: 18 }}>
        <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={goBack} style={{ width: 92, minHeight: 44, flexDirection: "row", gap: 7, alignItems: "center" }}>
          <Ionicons name="arrow-back" size={22} color="#26322D" />
          <Text style={{ color: "#26322D", fontWeight: "700", fontSize: 16 }}>Back</Text>
        </Pressable>

        <View style={{ gap: 7 }}>
          <Text style={{ fontSize: 32, fontWeight: "800", color: "#26322D" }}>Daily notes</Text>
          <Text style={{ color: "#68736E", lineHeight: 22 }}>A quiet place for reminders and thoughts.</Text>
        </View>

        <TextInput
          accessibilityLabel="Daily note"
          autoFocus
          multiline
          value={note}
          onChangeText={setNote}
          placeholder="Write a note…"
          placeholderTextColor="#A0A7A3"
          textAlignVertical="top"
          style={{ flex: 1, minHeight: 180, maxHeight: 420, borderWidth: 1, borderColor: "#E2E5E3", backgroundColor: "white", borderRadius: 16, padding: 18, color: "#26322D", fontSize: 17, lineHeight: 25 }}
        />

        <Text style={{ color: "#A0A7A3", textAlign: "right", fontSize: 12 }}>{note.length} characters • saved on this device</Text>
      </View>
    </KeyboardAvoidingView>
  </SafeAreaView>;
}
