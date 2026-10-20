function sigmoid(value){if(value>=0)return 1/(1+Math.exp(-value));const e=Math.exp(value);return e/(1+e)}
function couple(binary){const r=[[0,binary],[1-binary,0]],q=[[r[1][0]**2,-r[1][0]*r[0][1]],[-r[1][0]*r[0][1],r[0][1]**2]],p=[.5,.5],qp=[0,0];for(let iter=0;iter<100;iter++){let pqp=0;for(let t=0;t<2;t++){qp[t]=q[t][0]*p[0]+q[t][1]*p[1];pqp+=p[t]*qp[t]}if(Math.max(...qp.map(v=>Math.abs(v-pqp)))<.0025)break;for(let t=0;t<2;t++){const diff=(-qp[t]+pqp)/q[t][t];p[t]+=diff;pqp=(pqp+diff*(diff*q[t][t]+2*qp[t]))/(1+diff)/(1+diff);for(let j=0;j<2;j++){qp[j]=(qp[j]+diff*q[t][j])/(1+diff);p[j]/=1+diff}}}return p[1]}
export function probability(model,input){
  if(model.kind==='stacking')return probability(model.meta,Object.values(model.base).map(base=>probability(base,input)));
  let x=input.slice();
  for(const t of model.prep||[]){if(t.kind==='imputer')x=x.map((v,i)=>v==null||Number.isNaN(v)?t.values[i]:v);else if(t.kind==='scaler')x=x.map((v,i)=>(v-t.mean[i])/t.scale[i]);}
  if(model.kind==='LogisticRegression')return sigmoid(model.coef.reduce((sum,c,i)=>sum+c*x[i],model.intercept));
  if(model.kind==='SVC'){
    let d=model.intercept;
    for(let j=0;j<model.vectors.length;j++){let distance=0;for(let i=0;i<x.length;i++)distance+=(x[i]-model.vectors[j][i])**2;d+=model.dual[j]*Math.exp(-model.gamma*distance)}
    const f=d*model.a+model.b;const p=f>=0?Math.exp(-f)/(1+Math.exp(-f)):1/(1+Math.exp(f));return couple(Math.min(1-1e-7,Math.max(1e-7,p)));
  }
  if(model.kind==='GaussianNB'){
    const log=model.theta.map((theta,k)=>theta.reduce((sum,v,i)=>sum-.5*(Math.log(2*Math.PI*model.variance[k][i])+(x[i]-v)**2/model.variance[k][i]),Math.log(model.prior[k])));return sigmoid(log[1]-log[0]);
  }
  if(model.kind==='RandomForestClassifier'){
    x=x.map(Math.fround);return model.trees.reduce((sum,t)=>{let node=0;while(t.left[node]!==-1)node=x[t.feature[node]]<=t.threshold[node]?t.left[node]:t.right[node];const v=t.value[node];return sum+v[1]/(v[0]+v[1])},0)/model.trees.length;
  }
  if(model.kind==='KNeighborsClassifier'){
    const nearest=model.x.map((v,j)=>({i:j,d:Math.sqrt(v.reduce((sum,a,i)=>sum+(x[i]-a)**2,0))})).sort((a,b)=>a.d-b.d||a.i-b.i).slice(0,model.k);const zero=nearest.some(p=>p.d===0);let total=0,positive=0;for(const point of nearest){const w=zero?(point.d===0?1:0):1/point.d;total+=w;positive+=w*model.y[point.i]}return positive/total;
  }
  throw Error('MODEL_KIND_UNSUPPORTED');
}
export function predictAll(models,rows){return Object.fromEntries(Object.entries(models).map(([id,model])=>[id,rows.map(row=>{const p=probability(model,row);if(!Number.isFinite(p)||p<0||p>1)throw Error('NONFINITE_MODEL_OUTPUT');return p})]));}
