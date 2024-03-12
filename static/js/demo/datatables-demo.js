// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable();
});

$(document).ready(function() {
  $('#dataTableInspecao').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":5,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableReinspecao').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":5,
    order: [[0, 'desc']]
  });
});

$(document).ready(function() {
  $('#dataTableInspecionados').DataTable({
    "info":false,
    "aLengthMenu":[5,10,25],
    "iDisplayLength":5,
    order: [[0, 'desc']]
  });
});