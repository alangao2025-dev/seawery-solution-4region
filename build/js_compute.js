function compute(){
  const on = ITEMS.filter(enabled), ws = on.reduce((a,i)=>a+(+S.w[i.k]||0),0);
  const amt = {}; ITEMS.forEach(i=>amt[i.k]=0);
  if(ws>0) on.forEach(i=>amt[i.k]=S.total*(+S.w[i.k]||0)/ws);
  const P=S.p, fx=+P.fx||7.2, U=v=>v/fx, g=k=>amt[k]||0;
  const leads = {organic: +P.organic};
  ITEMS.forEach(i=>{ const a=g(i.k); if(!a||i.cpl==="none") return;
    leads[i.k] = i.cpl==="web" ? a/P.webCpl : i.cpl==="avg" ? U(a)/((P.cplS+(P.cplM||P.cplD))/2) : U(a)/P[i.cpl]; });
  const L = Object.values(leads).reduce((a,b)=>a+(isFinite(b)?b:0),0);
  const sql=L*P.sqlRate/100, samples=sql*P.sampleRate/100, wins=samples*P.winRate/100;
  const devUSD=wins*P.devFee, batchUSD=wins*P.volRate/100*P.batch, partUSD=L*P.partRate/100*P.partAov;
  const revUSD=devUSD+batchUSD+partUSD, rev=revUSD*fx, gp=rev*P.margin/100;
  const k = {leads:L, sql, samples, wins, revenue:rev, devrev:devUSD*fx, batchrev:batchUSD*fx, partrev:partUSD*fx, gp,
    cac: wins>0?S.total/wins:0, ltv:(P.devFee+P.volRate/100*P.batch*3)*P.margin/100*fx,
    mer: S.total>0?rev/S.total:0, coverage:S.total/COVER*100};
  k.ltvcac = k.cac>0 ? k.ltv/k.cac : 0;
  const reg={}; Object.keys(REG).forEach(r=>reg[r]=0);
  ITEMS.forEach(i=>Object.entries(i.reg).forEach(([r,f])=>reg[r]+=amt[i.k]*f));
  return {amt, leads, k, reg, fx};
}
