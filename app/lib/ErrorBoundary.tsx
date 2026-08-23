import { Component, type ErrorInfo, type ReactNode } from "react";
import { Pressable, SafeAreaView, Text, View } from "react-native";
import { colors } from "./ui";

export class AppErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(_error: Error, _info: ErrorInfo) { /* Never log safety-sensitive screen state. */ }
  render() { if (!this.state.failed) return this.props.children; return <SafeAreaView style={{ flex: 1, backgroundColor: colors.canvas }}><View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 14 }}><Text style={{ color: colors.ink, fontSize: 28, fontWeight: "900" }}>Shakti360 needs a fresh start</Text><Text style={{ color: colors.muted, lineHeight: 22 }}>Your active journey is stored locally and can be recovered when this screen reloads.</Text><Pressable onPress={() => this.setState({ failed: false })} style={{ backgroundColor: colors.primary, borderRadius: 16, padding: 16 }}><Text style={{ color: "white", fontWeight: "900", textAlign: "center" }}>Reload interface</Text></Pressable></View></SafeAreaView>; }
}
