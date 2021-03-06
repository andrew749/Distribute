var domain = 'http://' + document.domain + ':' + location.port;
var socket = io.connect(domain);
var context = this;

// connect with the server initially
socket.on('connect', function(socket) {
  console.log("connected");
});

// get registration event from server
socket.on('registration', function(data) {
  data = data;
  console.log("Got id:" + data['node_id']);
  context.node_id = data.node_id;
  document.getElementById('status-message').innerHTML = "Connected";
});

// get job and process it
socket.on('job_request', function(data){
  // got a job request from the server
  var payload_operation = data.payload_operation;
  var job_id = data.job_id;
  console.log("Got job with id " + job_id);

  var job_li = $('<li>')
    .addClass("list-group-item list-group-item-danger")
    .append(job_id);
  $('#job-status-list').append(job_li);

  var results;
  try {
    var results = executePayload(payload_operation);
    job_li.removeClass("list-group-item-danger");
    job_li.addClass("list-group-item-success");
    console.log("completed job");
  } catch(err) {
    socket.emit("job_results", {
      code : 1,
      node_id : context.node_id,
      message: err,
      job_id: context.job_id
    });
  }

  // return the calculated results
  socket.emit("job_results", {
    'code': 0,
    'node_id' : context.node_id,
    'results' : results,
    'job_id': job_id,
  });

  // execute payload and return result
  // TODO add a way to check status and close
  function executePayload(payload_operation, payload_data) {
    var results = new Function(payload_operation)();
    return results;
  }
});

window.onbeforeunload = function() {
  socket.emit('unregister', {'node_id': context.node_id});
}
