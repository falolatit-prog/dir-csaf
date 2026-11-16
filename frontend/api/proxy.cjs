const ALLOWED_GET=new Set(['health','dashboard','objects','cases','actions','audit']);
const ALLOWED_POST=new Set(['objects','observations','evidence','assessments','actions','observations/sync']);
function allowed(method,path){
 const p=path.replace(/^\/+|\/+$/g,'');
 if(method==='GET')return ALLOWED_GET.has(p)||/^risk\/[A-Za-z0-9._-]{1,128}$/.test(p);
 if(method==='POST')return ALLOWED_POST.has(p)||/^cases\/[A-Za-z0-9._-]{1,128}\/review$/.test(p)||/^actions\/[A-Za-z0-9._-]{1,128}\/transition$/.test(p);
 return false;
}
function authorize(header,expected){
 if(!expected||expected.length<16)return false;
 const provided=typeof header==='string'&&header.startsWith('Bearer ')?header.slice(7):'';
 const crypto=require('node:crypto');
 const a=crypto.createHash('sha256').update(provided).digest();
 const b=crypto.createHash('sha256').update(expected).digest();
 return crypto.timingSafeEqual(a,b);
}
function backendUrl(base,path){
 const u=new URL(base);
 if(u.protocol!=='https:'||u.username||u.password||u.search||u.hash)throw Error('BACKEND_URL must be an HTTPS base URL');
 const clean=path.replace(/^\/+|\/+$/g,'');
 if(!allowed('GET',clean)&&!allowed('POST',clean))throw Error('route not allowed');
 return new URL('/'+clean,u).toString();
}
module.exports={allowed,authorize,backendUrl};
