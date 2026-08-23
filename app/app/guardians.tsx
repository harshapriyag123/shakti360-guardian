import { useCallback, useEffect, useState } from "react";
import { Platform, Pressable, Share, Text, View } from "react-native";
import { authPost, get } from "../lib/api";
import { Action, Card, colors, ErrorBanner, Eyebrow, Field, Loading, Pill, Screen, Title } from "../lib/ui";

type Delivery = { channel: "sms" | "email"; status: "queued" | "failed" | "not_configured"; message: string };
type Guardian = { id: string; name: string; relationship: string; phone?: string; email?: string; priority: number; status: string; invite_token: string; invite_expires_at: string; journey_started: boolean; missed_checkin: boolean; sos: boolean; live_location: boolean; delivery?: Delivery[] };
type DeliveryResponse = { invite_url: string; deliveries: Delivery[] };

function ChannelChoice({ selected, icon, label, detail, onPress }: { selected: boolean; icon: string; label: string; detail: string; onPress: () => void }) {
  return <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: selected }} onPress={onPress} style={{ flex: 1, minWidth: 145, minHeight: 72, padding: 13, borderRadius: 16, borderWidth: 2, borderColor: selected ? colors.primary : colors.border, backgroundColor: selected ? colors.mint : "white", justifyContent: "center" }}><Text style={{ color: colors.ink, fontWeight: "900" }}>{selected ? "✓ " : ""}{icon} {label}</Text><Text style={{ color: colors.muted, fontSize: 12, marginTop: 4 }}>{detail}</Text></Pressable>;
}

function inviteLink(guardian: Guardian) {
  const base = process.env.EXPO_PUBLIC_APP_URL || (typeof window !== "undefined" ? window.location.origin : "https://shakti360.app");
  return `${base}/guardian-invite?token=${encodeURIComponent(guardian.invite_token)}`;
}

export default function Guardians() {
  const [items, setItems] = useState<Guardian[]>([]);
  const [name, setName] = useState("");
  const [relationship, setRelationship] = useState("Friend");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [sms, setSms] = useState(true);
  const [mail, setMail] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    try { const data = await get<{ guardians: Guardian[] }>("/guardians"); setItems(data.guardians); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not load guardians"); }
  }, []);
  useEffect(() => { load(); }, [load]);

  async function addAndSend() {
    try {
      setBusy(true); setError(""); setNotice("");
      const channels = [...(sms ? ["sms" as const] : []), ...(mail ? ["email" as const] : [])];
      const enteredPhone = phone.replace(/[\s()-]/g, "");
      const normalizedPhone = enteredPhone && !enteredPhone.startsWith("+") ? `+${enteredPhone}` : enteredPhone;
      const created = await authPost<Guardian>("/guardians", { name: name.trim(), relationship: relationship.trim(), phone: normalizedPhone || null, email: email.trim() || null, priority: Math.min(items.length + 1, 5), journey_started: true, missed_checkin: true, sos: true, live_location: true });
      const result = await authPost<DeliveryResponse>(`/guardians/${created.id}/send-invite`, { channels });
      const guardian = { ...created, delivery: result.deliveries, status: result.deliveries.some(item => item.status === "queued") ? "invite sent" : "share link ready" };
      setItems(value => [...value, guardian]); setName(""); setPhone(""); setEmail("");
      const failures = result.deliveries.filter(item => item.status !== "queued");
      setNotice(failures.length ? "The provider could not deliver this invitation. Its secure link is ready below—copy or share it directly." : "Invitation accepted by the selected delivery provider.");
    } catch (e) { setError(e instanceof Error ? e.message : "Could not send invitation"); }
    finally { setBusy(false); }
  }

  async function copyInvite(guardian: Guardian) {
    const url = inviteLink(guardian);
    try {
      if (Platform.OS === "web" && typeof navigator !== "undefined" && navigator.clipboard) await navigator.clipboard.writeText(url);
      else await Share.share({ title: "Shakti360 Guardian invitation", message: url });
      setNotice(`Invitation code for ${guardian.name} copied to the clipboard.`);
    } catch { setError("Could not copy the invitation. Use Share invitation instead."); }
  }

  async function shareInvite(guardian: Guardian) {
    const url = inviteLink(guardian);
    await Share.share({ title: "Shakti360 Guardian invitation", message: `${guardian.name}, you’re invited to be a temporary safety guardian. ${url}\nExpires ${new Date(guardian.invite_expires_at).toLocaleString()}` });
  }

  const valid = name.trim() && (sms || mail) && (!sms || phone.trim()) && (!mail || email.trim());
  return <Screen><Eyebrow>TRUSTED GUARDIAN CIRCLE</Eyebrow><Title subtitle="You decide who receives journey, missed check-in, SOS, and temporary location updates.">People you trust</Title><Card tone="mint"><Text style={{ color: colors.primaryDark, fontWeight: "900" }}>Session-based, never permanent</Text><Text style={{ color: colors.muted, lineHeight: 20 }}>Invitation links expire after 24 hours. Location access expires after each safety session.</Text></Card>
    {items.map((guardian, index) => <Card key={guardian.id}><View style={{ flexDirection: "row", justifyContent: "space-between", gap: 10 }}><View style={{ flex: 1 }}><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 17 }}>{guardian.name}</Text><Text style={{ color: colors.muted }}>{guardian.relationship} • Priority {index + 1}</Text><Text style={{ color: colors.muted, fontSize: 12, marginTop: 3 }}>{guardian.phone || guardian.email || "Share link only"}</Text></View><Pill label={guardian.status} tone={guardian.status === "invite sent" ? "green" : "gold"} /></View>
      {guardian.delivery?.map(item => <Text key={item.channel} style={{ color: item.status === "queued" ? colors.primary : colors.gold, fontSize: 13, fontWeight: "700" }}>{item.channel === "sms" ? "SMS" : "Email"}: {item.status === "queued" ? item.message : "Delivery was not accepted. Copy or share the secure invitation below."}</Text>)}
      <Text selectable style={{ color: colors.primaryDark, backgroundColor: colors.mint, borderRadius: 10, padding: 10, fontSize: 12 }} numberOfLines={2}>{inviteLink(guardian)}</Text>
      <View style={{ flexDirection: "row", gap: 9, flexWrap: "wrap" }}><View style={{ flex: 1, minWidth: 145 }}><Action label="Copy invitation code" icon="copy" variant="secondary" onPress={() => copyInvite(guardian)} /></View><View style={{ flex: 1, minWidth: 145 }}><Action label="Share invitation" icon="share" variant="secondary" onPress={() => shareInvite(guardian)} /></View></View>
    </Card>)}
    <Card><Text style={{ color: colors.ink, fontWeight: "900", fontSize: 20 }}>Add and invite a guardian</Text><Text style={{ color: colors.muted, lineHeight: 20 }}>Choose a provider, then keep the secure share link as a fallback.</Text><Field label="Name" value={name} onChangeText={setName} placeholder="Guardian name" autoComplete="name" /><Field label="Relationship" value={relationship} onChangeText={setRelationship} placeholder="Friend, parent, partner…" /><View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}><ChannelChoice selected={sms} icon="💬" label="Text message" detail="Delivered with Twilio" onPress={() => setSms(value => !value)} /><ChannelChoice selected={mail} icon="✉️" label="Email" detail="Delivered with Resend" onPress={() => setMail(value => !value)} /></View>{sms ? <Field label="Mobile number" value={phone} onChangeText={setPhone} placeholder="+1 555 123 4567" keyboardType="phone-pad" autoComplete="tel" /> : null}{mail ? <Field label="Email address" value={email} onChangeText={setEmail} placeholder="guardian@example.com" keyboardType="email-address" autoCapitalize="none" autoComplete="email" /> : null}<Text style={{ color: colors.muted, fontSize: 12 }}>Twilio trial accounts can send only to verified recipients. Use an international number beginning with + and country code.</Text><Action label="Create and send invitation" icon="send" onPress={addAndSend} disabled={busy || !valid} /></Card>
    {busy ? <Loading label="Sending through secure delivery providers…" /> : null}{notice ? <Card tone="mint"><Text accessibilityLiveRegion="polite" style={{ color: colors.primaryDark, lineHeight: 20, fontWeight: "700" }}>{notice}</Text></Card> : null}{error ? <ErrorBanner message={error} /> : null}<Text style={{ color: colors.muted, fontSize: 12, lineHeight: 18 }}>“Queued” means the provider accepted the message, not that the recipient opened it. Carrier and mailbox delivery can still fail.</Text></Screen>;
}
