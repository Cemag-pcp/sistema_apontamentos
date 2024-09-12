$('#modalPecas').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var code = button.data('code');
    var quantity = button.data('quantity'); 

    var modal = $(this);
    modal.find('.modal-body #codigoModal').text(code); 
    modal.find('.modal-body #quantidadeModal').text(quantity); 

    $.ajax({
        url: `/consultar-pecas-conjuntos?code=${code}&quantity=${quantity}`, 
        method: 'GET', 
        success: function(response) {
            console.log('Dados enviados com sucesso:', response);
            
            modal.modal('show');
        },
        error: function(xhr, status, error) {
            console.error('Erro ao enviar os dados:', error);
        }
    });
});
