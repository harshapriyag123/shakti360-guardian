import { useState } from "react";
import { SafeAreaView, ScrollView, Text, Pressable, View } from "react-native";
import { get } from "../lib/api";

export default function Patterns(){
  const [result,setResult]=useState<any>(null);
  return <SafeAreaView style={{flex:1}}><ScrollView contentContainerStyle={{padding:20,gap:12}}>
    <Text style={{fontSize:26,fontWeight:"800"}}>Pattern Intelligence</Text>
    <Text style={{opacity:.7}}>Descriptive analysis across user-recorded incidents — not guilt or danger prediction.</Text>
    <Pressable onPress={async()=>setResult(await get("/incidents/patterns"))} style={{padding:16,borderWidth:1,borderRadius:12}}><Text style={{fontWeight:"800"}}>Analyze patterns</Text></Pressable>
    {result && <View style={{padding:16,borderWidth:1,borderRadius:12}}>
      <Text>Incidents: {result.incident_count}</Text>
      {result.observations.length ? result.observations.map((o:string)=><Text key={o}>• {o}</Text>) : <Text>Not enough repeated signals yet.</Text>}
      <Text style={{marginTop:8,opacity:.6}}>{result.disclaimer}</Text>
    </View>}
  </ScrollView></SafeAreaView>
}
