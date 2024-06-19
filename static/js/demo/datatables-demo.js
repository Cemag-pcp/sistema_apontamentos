// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable();
});

$(document).ready(function() {
  $('#dataTableInspecao').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableReinspecao').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableInspecionados').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableAinspecionarSolda').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableInspecionadosSolda').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableReinspecaoSolda').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableAinspecionarEstamparia').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableinspecionadosEstamparia').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableReinspecaoEstamparia').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});dataTableRetesteSolda

$(document).ready(function() {
  $('#dataTableRetesteSolda').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":10,
    order: [[0, 'desc']]
  });
});