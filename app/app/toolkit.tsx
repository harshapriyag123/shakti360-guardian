import { Link } from "expo-router";
import { Pressable, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Card, colors, Eyebrow, Screen, Title } from "../lib/ui";
const tools = [
  ["shield-checkmark", "Safety readiness", "Personalized setup score and next actions", "/readiness"],
  ["chatbubble-ellipses", "Scam Shield", "Explain suspicious language and links", "/cyber"],
  ["document-lock", "Evidence Vault", "Structure records without inferring intent", "/evidence"],
  ["finger-print", "Privacy Center", "Review permissions and data exposure", "/privacy"],
  ["receipt", "Privacy Receipts", "See exactly what each journey shared", "/receipts"],
  ["analytics", "Pattern insights", "See patterns only in events you recorded", "/patterns"],
  ["call", "Fake call", "Schedule an escape-assistance call screen", "/fake-call"],
  ["flask", "Judge mode", "See the safety architecture and live demo flow", "/judge"],
] as const;
export default function Toolkit() { return <Screen><Eyebrow>PREVENT • RESPOND • RECOVER</Eyebrow><Title subtitle="Every tool explains what it does and what it cannot do.">Safety toolkit</Title>{tools.map(([icon, title, copy, href]) => <Link key={href} href={href as any} asChild><Pressable><Card><View style={{ flexDirection: "row", alignItems: "center", gap: 14 }}><View style={{ width: 46, height: 46, borderRadius: 15, backgroundColor: colors.mint, alignItems: "center", justifyContent: "center" }}><Ionicons name={icon} size={23} color={colors.primary} /></View><View style={{ flex: 1 }}><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 17 }}>{title}</Text><Text style={{ color: colors.muted, lineHeight: 20, marginTop: 3 }}>{copy}</Text></View><Ionicons name="chevron-forward" size={20} color={colors.muted} /></View></Card></Pressable></Link>)}</Screen>; }
