import React, {useEffect,useState} from 'react';
import {Alert,Image,KeyboardAvoidingView,Platform,SafeAreaView,ScrollView,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {StatusBar} from 'expo-status-bar';
const {add,markSynced,pending}=require('./src/queue.cjs');
const STORAGE_KEY='dircsaf.field.queue.v1';
const SETTINGS_KEY='dircsaf.field.api.v1';
function Button({title,onPress,disabled=false}){return <TouchableOpacity accessibilityRole="button" disabled={disabled} onPress={onPress} style={[styles.button,disabled&&{opacity:0.5}]}><Text style={styles.buttonText}>{title}</Text></TouchableOpacity>}
function Field({label,value,onChangeText,placeholder,autoCapitalize='sentences'}){return <View style={styles.field}><Text style={styles.label}>{label}</Text><TextInput style={styles.input} value={value} onChangeText={onChangeText} placeholder={placeholder} autoCapitalize={autoCapitalize} /></View>}
export default function App(){
 const [apiUrl,setApiUrl]=useState('');
 const [token,setToken]=useState('');
 const [objectId,setObjectId]=useState('');
 const [location,setLocation]=useState('');
 const [observer,setObserver]=useState('');
 const [evidence,setEvidence]=useState('');
 const [photo,setPhoto]=useState(null);
 const [queue,setQueue]=useState([]);
 const [busy,setBusy]=useState(false);
 const [message,setMessage]=useState('Field observations are not identity confirmations.');
 useEffect(()=>{(async()=>{try{
   const saved=await AsyncStorage.getItem(STORAGE_KEY);
   if(saved)setQueue(JSON.parse(saved));
   const url=await AsyncStorage.getItem(SETTINGS_KEY);
   if(url)setApiUrl(url);
 }catch(e){setMessage('Unable to load locally saved observations: '+e.message)}})()},[]);
 async function persist(next){await AsyncStorage.setItem(STORAGE_KEY,JSON.stringify(next));setQueue(next)}
 async function capture(){
   const permission=await ImagePicker.requestCameraPermissionsAsync();
   if(!permission.granted){Alert.alert('Camera permission required','Enable camera permission to capture collection photographs.');return}
   const result=await ImagePicker.launchCameraAsync({quality:0.7,allowsEditing:false});
   if(!result.canceled)setPhoto(result.assets[0].uri);
 }
 async function save(){
   try{
     const localId='obs-'+Date.now()+'-'+Math.random().toString(36).slice(2);
     const next=add(queue,{local_id:localId,object_id:objectId.trim(),observed_location:location.trim(),
       observer:observer.trim(),evidence_ref:evidence.trim(),photo_uri:photo,
       captured_at:new Date().toISOString()});
     await persist(next);setObjectId('');setLocation('');setEvidence('');setPhoto(null);
     setMessage('Observation queued locally. Photo stays on this device and is NOT uploaded.');
   }catch(e){Alert.alert('Cannot save observation',e.message)}
 }
 async function sync(){
   if(busy)return;
   if(!apiUrl.trim()||!token.trim()){Alert.alert('API settings required','Enter the reachable API URL and development access token.');return}
   if(!/^https?:\/\//i.test(apiUrl.trim())){Alert.alert('Invalid URL','Enter a full http:// or https:// URL.');return}
   setBusy(true);
   let current=queue;
   try{
     for(const item of pending(current)){
       const response=await fetch(apiUrl.replace(/\/$/,'')+'/observations',{
         method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
         body:JSON.stringify({object_id:item.object_id,observed_location:item.observed_location,
           observer:item.observer,evidence_ref:item.evidence_ref})});
       const result=await response.json();
       if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
       current=markSynced(current,item.local_id,result);
       await persist(current);
     }
     await AsyncStorage.setItem(SETTINGS_KEY,apiUrl);
     setMessage('Observation metadata synchronized. Photographs remain local; identity is unverified.');
   }catch(e){setMessage('Synchronization stopped. Remaining observations stay queued: '+e.message)}
   finally{setBusy(false)}
 }
 return <SafeAreaView style={styles.root}><StatusBar style="light"/><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
   <View style={styles.header}><Text style={styles.heading}>DIR-CSAF</Text><Text style={styles.subtitle}>EVIDENCE | ACCOUNTABILITY | HUMAN REVIEW</Text><Text style={styles.headerSmall}>Field Verification</Text></View>
   <Text style={styles.notice}>{message}</Text>
   <Text style={styles.section}>Record physical observation</Text>
   <Field label="Collection object ID" value={objectId} onChangeText={setObjectId} autoCapitalize="characters" placeholder="e.g. OBJ-001"/>
   <Field label="Observed location" value={location} onChangeText={setLocation} placeholder="e.g. Storage Room B"/>
   <Field label="Observer" value={observer} onChangeText={setObserver} placeholder="Staff name or identifier"/>
   <Field label="Evidence reference" value={evidence} onChangeText={setEvidence} placeholder="Independent field note or identifier"/>
   <Button title="Capture photograph" onPress={capture}/>
   {photo&&<View><Image source={{uri:photo}} style={styles.preview}/><Text style={styles.hint}>Photograph is local only. It is not transmitted by synchronization.</Text></View>}
   <Button title="Save observation offline" onPress={save}/>
   <Text style={styles.section}>Synchronization</Text>
   <Field label="API base URL (reachable from this device)" value={apiUrl} onChangeText={setApiUrl} placeholder="http://192.168.1.10:8765" autoCapitalize="none"/>
   <Field label="Development bearer token (not stored)" value={token} onChangeText={setToken} placeholder="Enter session token" autoCapitalize="none"/>
   <Text style={styles.hint}>The API currently uses development-only authentication. Do not use real collection data or expose the server publicly.</Text>
   <Button title={busy?'Synchronizing...':'Synchronize queued observations'} onPress={sync} disabled={busy}/>
   <Text style={styles.section}>Local observation queue</Text>
   <Text style={styles.hint}>{pending(queue).length} pending of {queue.length} locally saved observations</Text>
   {queue.slice().reverse().map(item=><View key={item.local_id} style={styles.queueItem}><Text style={styles.queueTitle}>{item.object_id} | {item.observed_location}</Text><Text>{item.sync_status==='synced'?'Metadata synchronized':'Pending sync'}</Text><Text style={styles.hint}>Photo: {item.photo_uri?'stored locally':'none'}</Text></View>)}
 </ScrollView></SafeAreaView>
}
const styles=StyleSheet.create({
 root:{flex:1,backgroundColor:'#f4f7fb'},content:{paddingBottom:36},header:{backgroundColor:'#245485',padding:24},
 heading:{color:'white',fontSize:28,fontWeight:'bold'},subtitle:{color:'#e2edfa',fontSize:12,marginTop:6},headerSmall:{color:'white',fontSize:16,marginTop:14},
 notice:{margin:16,padding:14,backgroundColor:'#fff4d9',color:'#60471e',borderRadius:10},
 section:{fontSize:18,fontWeight:'bold',color:'#17324d',marginHorizontal:16,marginTop:20,marginBottom:8},
 field:{marginHorizontal:16,marginTop:10},label:{color:'#31485e',fontSize:13,marginBottom:5},
 input:{borderWidth:1,borderColor:'#bdccda',backgroundColor:'white',borderRadius:8,padding:12,fontSize:16},
 button:{marginHorizontal:16,marginTop:14,backgroundColor:'#245485',borderRadius:9,padding:14,alignItems:'center'},
 buttonText:{color:'white',fontWeight:'600'},preview:{height:170,margin:16,borderRadius:8},hint:{marginHorizontal:16,color:'#627487',fontSize:12,marginTop:6},
 queueItem:{marginHorizontal:16,marginTop:8,padding:12,backgroundColor:'white',borderRadius:9,borderWidth:1,borderColor:'#e0e8f0'},
 queueTitle:{fontWeight:'600',color:'#17324d'}
});
