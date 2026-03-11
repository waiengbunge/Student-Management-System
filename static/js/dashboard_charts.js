document.addEventListener('DOMContentLoaded', function(){
  function initLine(id, labels, data, label){
    const el = document.getElementById(id); if(!el) return;
    new Chart(el,{type:'line',data:{labels:labels,datasets:[{label:label,data:data,fill:true,backgroundColor:'rgba(54,162,235,0.12)',borderColor:'rgb(54,162,235)',tension:0.3}]},options:{responsive:true,plugins:{legend:{display:false}}}});
  }

  function initBar(id, labels, data, label){
    const el = document.getElementById(id); if(!el) return;
    new Chart(el,{type:'bar',data:{labels:labels,datasets:[{label:label,data:data,backgroundColor:'rgba(75,192,192,0.6)'}]},options:{responsive:true,plugins:{legend:{display:false}}}});
  }

  function initDoughnut(id, labels, data){
    const el = document.getElementById(id); if(!el) return;
    new Chart(el,{type:'doughnut',data:{labels:labels,datasets:[{data:data,backgroundColor:['#36a2eb','#ff6384','#ffcd56','#4bc0c0']}]},options:{responsive:true}});
  }

  // Example initializations (will only run if canvases exist)
  initLine('attendanceChart',['Week1','Week2','Week3','Week4'],[85,88,90,92],'Attendance %');
  initLine('gradeProgressChart',['Week1','Week2','Week3','Week4'],[65,70,75,78],'Grade');
  initBar('classAttendanceChart',['Class A','Class B','Class C'],[40,50,30],'Attendance');
  initDoughnut('programDistribution',['Prog A','Prog B','Prog C'],[45,30,25]);
});
