const {allowed,authorize,backendUrl}=require('./proxy.cjs');
module.exports=async function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 res.setHeader('X-Content-Type-Options','nosniff');
 const path=(Array.isArray(req.query.path)?req.query.path:[]).join('/');
 if(!allowed(req.method,path))return res.status(404).json({error:'Route unavailable'});
 if(!process.env.DIRCSAF_DASHBOARD_TOKEN||!authorize(req.headers.authorization,process.env.DIRCSAF_DASHBOARD_TOKEN))
   return res.status(401).json({error:'Dashboard authorization required'});
 if(!process.env.DIRCSAF_BACKEND_URL||!process.env.DIRCSAF_BACKEND_TOKEN)
   return res.status(503).json({error:'Backend not configured'});
 try{
   const url=backendUrl(process.env.DIRCSAF_BACKEND_URL,path);
   const controller=new AbortController();
   const timeout=setTimeout(()=>controller.abort(),8000);
   try{
     const body=req.method==='POST'?JSON.stringify(req.body||{}):undefined;
     if(body&&Buffer.byteLength(body)>250000)return res.status(413).json({error:'Request too large'});
     const response=await fetch(url,{method:req.method,headers:{Authorization:'Bearer '+process.env.DIRCSAF_BACKEND_TOKEN,...(body?{'Content-Type':'application/json'}:{})},body,signal:controller.signal,redirect:'error'});
     const text=await response.text();
     if(text.length>1000000)return res.status(502).json({error:'Backend response too large'});
     res.status(response.status).setHeader('Content-Type','application/json');
     try{return res.send(JSON.stringify(JSON.parse(text)))}catch{return res.send(JSON.stringify({error:'Invalid backend response'}))}
   }finally{clearTimeout(timeout)}
 }catch(e){return res.status(502).json({error:'Backend unavailable or misconfigured'})}
};
