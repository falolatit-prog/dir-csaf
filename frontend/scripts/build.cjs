const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
fs.mkdirSync(path.join(root,'dist'),{recursive:true});
for(const name of ['index.html','styles.css','app.js']){
 fs.copyFileSync(path.join(root,'public',name),path.join(root,'dist',name));
}
console.log('DIR-CSAF static frontend built');
