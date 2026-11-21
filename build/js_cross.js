const TRN={US:"美国·电机",US2:"美国·开发与代工",DE:"德国",VN:"越南",TH:"泰国",ID:"印尼",AE:"阿联酋",TR:"土耳其",JP:"日本",KR:"韩国"};
function drawCross(){
  const box=document.getElementById("crossChart"); if(!box||!CHART.cross) return; box.innerHTML="";
  const d=CHART.cross, rows=d.rows.filter(r=>!SKIPC.includes(r.c)), NM={US:"美国",DE:"德国",TR:"土耳其",VN:"越南",AE:"阿联酋",SA:"沙特",IR:"伊朗",JP:"日本",KR:"韩国"};
  const W=1000,rowH=30,L=90,H=rows.length*rowH+40, mx=Math.max(.05,...rows.flatMap(r=>r.v)), bw=(rowH-8)/d.terms.length;
  const svg=svgBox(W,H), x=v=>L+(W-L-60)*v/mx;
  rows.forEach((r,i)=>{const y0=10+i*rowH;
    svg.appendChild(el("text",{x:L-8,y:y0+rowH/2,"text-anchor":"end","font-size":12,fill:"#18202f"},NM[r.c]||r.c));
    r.v.forEach((v,j)=>{svg.appendChild(el("rect",{x:L,y:y0+j*bw,width:Math.max(1,x(v)-L),height:bw-1,fill:COLS[j%5],opacity:.85}));
      svg.appendChild(el("text",{x:x(v)+4,y:y0+j*bw+bw-2,"font-size":10,fill:"#5d6b82"},v.toFixed(2)));});});
  box.appendChild(svg);
  const lg=document.createElement("div"); lg.className="legend";
  d.terms.forEach((t,j)=>{const s=document.createElement("span"); const i=document.createElement("i"); i.style.background=COLS[j%5]; s.appendChild(i); s.appendChild(document.createTextNode(t)); lg.appendChild(s);});
  const n=document.createElement("span"); n.textContent="数值 = 该词近 12 个月均值 ÷ 同组 PLC 均值"; lg.appendChild(n); box.appendChild(lg);
}
