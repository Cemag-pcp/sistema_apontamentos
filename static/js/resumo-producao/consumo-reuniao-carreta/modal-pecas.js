$('#modalPecas').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var code = button.data('code');
    var quantity = button.data('quantity'); 

    var modal = $(this);
    modal.find('.modal-body #codigoModal').text(code); 
    modal.find('.modal-body #quantidadeModal').text(quantity); 
});
