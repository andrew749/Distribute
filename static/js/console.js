var editor = ace.edit("code-text");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/javascript");
editor.setValue(Cookies.get('code'));

function updateRangeBox(value) {
  document.getElementById("range-slider").innerHTML =  value;
}

$('#dispatch-button').click(function(evt){
  var code = editor.getValue();
  var node_count = $('#node-count-input').val();
  dispatchJob(code, node_count);
});

function getRunningJobs() {
  $.get('/running_jobs', function(data){
    $('#job-list').empty();
    for (var x in data) {
      var element = data[x];
      $.get("/get-job-status/"+ element.id, function(result){
        $('#job-list')
          .append(
            $('<li>')
            .addClass(classForState(element.success))
            .addClass('label list-group-item')
              .append(element.id + " : " + result.status + "%")
          );
      });
    }
  });
}

function dispatchJob(code, number_of_nodes) {
  $.ajax({
    type: 'POST',
    url:'/dispatch_job',
    contentType: 'application/json',
    data: JSON.stringify({
      code : code,
      number_of_nodes: number_of_nodes
    })});
}

function classForState(state) {
  return state ? 'list-group-item-success' : 'list-group-item-danger' ;
}

function fetchNodeCount() {
  $.get('/node_counts', function(data){
    updateNodeCount(data.free_nodes, data.occupied_nodes)
  });
}

function updateNodeCount(freeNodes, nodesInUse) {
  $('#connected-nodes').text(freeNodes + nodesInUse);
  $('#free-nodes').text(freeNodes);
  $('#processing-nodes').text(nodesInUse);
  $('#node-count-input').attr('max', freeNodes);
  console.log(freeNodes, nodesInUse);
}

function pollNodeStats() {
  setInterval(function(){
    getRunningJobs();
    fetchNodeCount();
    Cookies.set('code', editor.getValue() );
  }, 5000);
}

pollNodeStats();

