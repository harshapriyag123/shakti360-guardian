import { useCallback, useEffect, useState } from "react";
import { Link } from "expo-router";
import { Pressable, RefreshControl, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { get } from "../lib/api";
import { Card, colors, ErrorBanner, Eyebrow, Metric, Pill, Screen, Title } from "../lib/ui";
import { PWAInstall } from "../lib/PWAInstall";
import { getCurrentUser } from "../lib/authClient";

type Impact = { journeys_started: number; cyber_scans: number; incidents_documented: number };
type SessionUser = { preferred_name: string; email: string };
const tools = [
  { icon: "shield-checkmark", title: "Safety readiness", copy: "Find gaps in your safety setup", href: "/readiness", color: "#EAF3FF" },
  { icon: "chatbubble-ellipses", title: "Scam scanner", copy: "Check a suspicious message", href: "/cyber", color: "#FFF1E8" },
  { icon: "document-lock", title: "Evidence vault", copy: "Document events privately", href: "/evidence", color: "#F1EDFF" },
  { icon: "location", title: "Nearby support", copy: "Use your live location", href: "/resources", color: "#E7F7F0" },
] as const;

function AuthWelcome({ checking }: { checking: boolean }) {
  const benefits = [
    ["navigate", "Temporary journeys", "Share only while a journey is active"],
    ["people", "Guardian Circle", "You choose who receives each update"],
    ["finger-print", "Privacy receipts", "See what was shared and for how long"],
  ] as const;
  return <Screen><View style={{ alignItems: "center", gap: 10, paddingTop: 16 }}><View style={{ width: 74, height: 74, borderRadius: 24, backgroundColor: colors.primaryDark, alignItems: "center", justifyContent: "center" }}><Ionicons name="shield-checkmark" size={39} color={colors.lime} /></View><Eyebrow>SHAKTI360 GUARDIAN</Eyebrow><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 37, lineHeight: 43, textAlign: "center", maxWidth: 580 }}>Your safety, your control.</Text><Text style={{ color: colors.muted, fontSize: 17, lineHeight: 25, textAlign: "center", maxWidth: 590 }}>Prepare, stay connected, and access support without permanent surveillance.</Text></View><PWAInstall /><View style={{ flexDirection: "row", flexWrap: "wrap", gap: 14 }}>{benefits.map(([icon,title,copy]) => <Card key={title} style={{ flex: 1, minWidth: 190 }}><View style={{ width: 44, height: 44, borderRadius: 14, backgroundColor: colors.mint, alignItems: "center", justifyContent: "center" }}><Ionicons name={icon} size={23} color={colors.primary} /></View><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 17 }}>{title}</Text><Text style={{ color: colors.muted, lineHeight: 20 }}>{copy}</Text></Card>)}</View><Card tone="dark" style={{ padding: 22 }}><Text style={{ color: "white", fontWeight: "900", fontSize: 23 }}>Start with a private account</Text><Text style={{ color: "#C9DED6", lineHeight: 21 }}>Your account uses an Argon2-protected password and secure browser sessions.</Text><Link href="/register" asChild><Pressable style={{ backgroundColor: colors.lime, borderRadius: 16, minHeight: 54, paddingHorizontal: 18, justifyContent: "center", alignItems: "center" }}><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 16 }}>Create my account</Text></Pressable></Link><Link href="/login" asChild><Pressable style={{ backgroundColor: "white", borderRadius: 16, minHeight: 54, paddingHorizontal: 18, justifyContent: "center", alignItems: "center" }}><Text style={{ color: colors.primaryDark, fontWeight: "900", fontSize: 16 }}>I already have an account</Text></Pressable></Link></Card><Link href="/explore" asChild><Pressable style={{ minHeight: 48, justifyContent: "center" }}><Text style={{ color: colors.primary, fontWeight: "800", textAlign: "center" }}>Explore the working product first →</Text></Pressable></Link>{checking ? <Text style={{ color: colors.muted, fontSize: 12, textAlign: "center" }}>Checking for an existing secure session…</Text> : null}<Text style={{ color: colors.muted, fontSize: 12, textAlign: "center", lineHeight: 18 }}>Shakti360 does not guarantee safety or replace emergency services.</Text></Screen>;
}

function Dashboard() {
  const [impact, setImpact] = useState<Impact | null>(null);
  const [online, setOnline] = useState(false);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const load = useCallback(async () => {
    try { setError(""); const [, stats] = await Promise.all([get("/health"), get<Impact>("/analytics/impact")]); setImpact(stats); setOnline(true); }
    catch (e) { setOnline(false); setError(e instanceof Error ? e.message : "Backend unavailable"); }
    finally { setRefreshing(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  return <Screen refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={colors.primary} />}>
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
      <View><Eyebrow>SHAKTI360</Eyebrow><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 21 }}>Your safety, your control.</Text></View>
      <Link href="/profile" asChild><Pressable accessibilityLabel="Open profile" style={{ width: 44, height: 44, borderRadius: 22, backgroundColor: colors.mint, alignItems: "center", justifyContent: "center" }}><Ionicons name="person" size={22} color={colors.primary} /></Pressable></Link>
    </View>
    <PWAInstall />
    <Card tone="dark" style={{ padding: 22, gap: 16 }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between" }}><Pill label={online ? "Protection online" : "Offline mode"} tone={online ? "green" : "gold"} /><Ionicons name="shield-checkmark" size={36} color={colors.lime} /></View>
      <View><Text style={{ color: "white", fontSize: 28, lineHeight: 34, fontWeight: "900" }}>Heading somewhere?</Text><Text style={{ color: "#C9DED6", fontSize: 15, lineHeight: 22, marginTop: 6 }}>Start a timed journey. We adapt check-ins to your battery and escalate only by your rules.</Text></View>
      <Link href="/journey" asChild><Pressable style={{ backgroundColor: colors.lime, borderRadius: 16, padding: 16, flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 16 }}>Start a safe journey</Text><Ionicons name="arrow-forward" size={20} color={colors.ink} /></Pressable></Link>
      <Text style={{ color: "#AFCBC0", fontSize: 12 }}>Private by design • Temporary location session</Text>
    </Card>
    {error ? <ErrorBanner message="Start the FastAPI backend on port 8000 to enable live protection and metrics." retry={load} /> : null}
    <View style={{ gap: 10 }}><Title subtitle="Simple tools for the moments that matter">Your safety toolkit</Title>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>{tools.map(item => <Link key={item.href} href={item.href as any} asChild><Pressable style={({ pressed }) => ({ width: "48%", minWidth: 150, flexGrow: 1, backgroundColor: "white", borderWidth: 1, borderColor: colors.border, borderRadius: 20, padding: 16, gap: 11, opacity: pressed ? .7 : 1 })}><View style={{ width: 42, height: 42, borderRadius: 13, backgroundColor: item.color, alignItems: "center", justifyContent: "center" }}><Ionicons name={item.icon} size={22} color={colors.primaryDark} /></View><Text style={{ fontWeight: "900", fontSize: 16, color: colors.ink }}>{item.title}</Text><Text style={{ color: colors.muted, lineHeight: 19 }}>{item.copy}</Text></Pressable></Link>)}</View>
    </View>
    <Card tone="mint"><View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}><View><Eyebrow>LIVE PILOT IMPACT</Eyebrow><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 20, marginTop: 4 }}>Protection in action</Text></View><Link href="/impact" asChild><Pressable><Ionicons name="arrow-forward-circle" size={31} color={colors.primary} /></Pressable></Link></View><View style={{ flexDirection: "row", gap: 8 }}><Metric value={impact?.journeys_started ?? "—"} label="journeys started" /><Metric value={impact?.cyber_scans ?? "—"} label="scams checked" /><Metric value={impact?.incidents_documented ?? "—"} label="records secured" /></View></Card>
    <View style={{ gap: 8 }}><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 18 }}>More control</Text><View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>{[{ t: "Pattern insights", h: "/patterns" }, { t: "Privacy check", h: "/privacy" }].map(x => <Link key={x.h} href={x.h as any} asChild><Pressable style={{ backgroundColor: "white", borderColor: colors.border, borderWidth: 1, paddingVertical: 12, paddingHorizontal: 15, borderRadius: 999 }}><Text style={{ color: colors.ink, fontWeight: "700" }}>{x.t}</Text></Pressable></Link>)}</View></View>
    <Text style={{ color: colors.muted, fontSize: 12, lineHeight: 18, textAlign: "center" }}>AI assists. You decide. Shakti360 does not replace emergency services.</Text>
  </Screen>;
}

export default function Home() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [checking, setChecking] = useState(true);
  useEffect(() => { getCurrentUser<SessionUser>().then(setUser).catch(() => setUser(null)).finally(() => setChecking(false)); }, []);
  return user ? <Dashboard /> : <AuthWelcome checking={checking} />;
}
