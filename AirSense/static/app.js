let chart;
const $ = id => document.getElementById(id);
function fmt(v){return v===null||v===undefined?"—":Number(v).toFixed(1)}
function showError(msg){$("error").textContent=msg;$("error").classList.remove("hidden")}
function hideError(){$("error").classList.add("hidden")}
async function load(){
  hideError(); const city=$("city").value; $("refresh").textContent="Loading…";
  try{
    const res=await fetch(`/api/air-quality?city=${encodeURIComponent(city)}`);
    if(!res.ok){const e=await res.json();throw new Error(e.detail||"Unable to load air quality data")}
    const d=await res.json(), c=d.current, p=d.prediction;
    $("heroCity").textContent=city.toUpperCase();$("aqi").textContent=c.aqi_estimate??"—";
    $("category").textContent=c.category;$("advice").textContent=c.advice;
    $("pm25").textContent=fmt(c.pm25);$("pm10").textContent=fmt(c.pm10);
    $("no2").textContent=fmt(c.no2);$("o3").textContent=fmt(c.o3);
    $("prediction").innerHTML=p.next_hour_pm25===null?"—":`${fmt(p.next_hour_pm25)}<small>µg/m³</small>`;
    $("modelStatus").textContent=p.model_available?"Trained Random Forest model loaded":"Model not trained yet — follow README training steps";
    $("healthInsight").textContent=`${c.category}: ${c.advice}. Check official CPCB updates for authoritative local readings and follow local health guidance.`;
    $("updated").textContent="Updated "+new Date().toLocaleTimeString();
    drawChart(d.hourly||[]);
  }catch(e){showError(e.message);$("updated").textContent="Data unavailable"}
  finally{$("refresh").textContent="↻ Refresh"}
}
function drawChart(rows){
  const ctx=$("trendChart").getContext("2d");
  const labels=rows.map(x=>new Date(x.time).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"}));
  const config={type:"line",data:{labels,datasets:[
    {label:"PM2.5",data:rows.map(x=>x.pm25),borderColor:"#167553",backgroundColor:"#16755318",fill:true,tension:.35,pointRadius:0,borderWidth:2},
    {label:"PM10",data:rows.map(x=>x.pm10),borderColor:"#8c83db",backgroundColor:"transparent",tension:.35,pointRadius:0,borderWidth:2}
  ]},options:{responsive:true,plugins:{legend:{labels:{boxWidth:8,usePointStyle:true,font:{size:10}}}},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:6,font:{size:9}}},y:{grid:{color:"#eef2ef"},ticks:{font:{size:9}}}}}};
  if(chart)chart.destroy();chart=new Chart(ctx,config);
}
$("refresh").addEventListener("click",load);$("city").addEventListener("change",load);load();
