import { useEffect, useState } from "react";
import { SafeAreaView, ScrollView, Text, View, Pressable } from "react-native";
import { get, post } from "../lib/api";

export default function Impact(){
  const [impact,setImpact]=useState<any>(null);
  async function refresh(){ setImpact(await get("/analytics/impact")); }
  useEffect(()=>{refresh()},[]);
  async function addDemoFeedback(){ await post("/feedback",{rating:5,useful:true,text:"Demo feedback"}); await refresh(); }
  const cards = impact ? [
    ["Journeys started",impact.journeys_started],
    ["Journeys completed",impact.journeys_completed],
    ["Cyber scans",impact.cyber_scans],
    ["Incidents documented",impact.incidents_documented],
    ["Readiness checks",impact.readiness_checks],
    ["Feedback",impact.feedback_count],
    ["Average rating",impact.average_rating ?? "-"]
  ] : [];
  return <SafeAreaView style={{flex:1}}><ScrollView contentContainerStyle={{padding:20,gap:12}}>
    <Text style={{fontSize:26,fontWeight:"800"}}>Impact Dashboard</Text>
    <Text style={{opacity:.7}}>Turn DoraHacks 50-user validation into measurable product proof.</Text>
    {cards.map(([label,value])=><View key={label as string} style={{padding:16,borderWidth:1,borderRadius:12}}><Text style={{fontSize:26,fontWeight:"800"}}>{String(value)}</Text><Text>{label}</Text></View>)}
    <Pressable onPress={addDemoFeedback} style={{padding:16,borderWidth:1,borderRadius:12}}><Text style={{fontWeight:"800"}}>Add demo feedback</Text></Pressable>
  </ScrollView></SafeAreaView>
}
