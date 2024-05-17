// Array com as causas
var causas = ["Faltando Solda", "Olho de Peixe", "Arranhão", "Escorrimento", "Empoeiramento","Casca de Laranja","Manchas",
"Contato","Amassando","Camada Baixa","Corrosão","Marcação por Água","Marcação por Óleo","Tonalidade","Marca texto industrial","Respingo de Solda",
"Marcação de Peça","Falta de aderência","Decapante","Desplacamento","Água"];

function adicionarSelects(n_nao_conformidades,coluna_causa) {
    
    var n_nao_conformidades = document.getElementById(n_nao_conformidades).value;
    var coluna_causa = document.getElementById(coluna_causa);

    coluna_causa.innerHTML = "";

    var div_row = document.createElement('div');
    div_row.className = 'row';

    if (n_nao_conformidades > 0) {
        coluna_causa.style.display = 'block';
        for (var i = 1; i <= n_nao_conformidades; i++) {
            var div = document.createElement("div");
            div.className = "col-sm-6 mb-4";

            var label = document.createElement("label");
            label.textContent = "Causa " + i;

            var select = document.createElement("select");
            select.name = "causa_reinspecao_" + i;
            select.id = "causa_reinspecao_" + i;
            select.className = "form-control";

            // Adiciona a opção vazia
            var optionHidden = document.createElement("option");
            optionHidden.value = "";
            optionHidden.selected = true;
            optionHidden.hidden = true;
            select.appendChild(optionHidden);

            // Adiciona as opções das causas do array
            for (var j = 0; j < causas.length; j++) {
                var option = document.createElement("option");
                option.value = causas[j];
                option.textContent = causas[j];
                select.appendChild(option);
            }

            var campoArquivos = criandoHTMLFiles(i)

            div.appendChild(label);
            div.appendChild(select);
            div_row.append(div,campoArquivos)
            coluna_causa.appendChild(div_row);
        }
        coluna_causa.querySelectorAll('[id^="foto_inspecao_"]').forEach(function(inputElement) {
            inputElement.addEventListener("change", function() {
                var files = this.files;
                var label = this.parentNode.querySelector('.custom-file-label'); // Obter a label correspondente
                var fileNames = [];
                for (var i = 0; i < files.length; i++) {
                    fileNames.push(files[i].name);
                }
                if (files.length == 1) {
                    label.textContent = "Possui " + files.length + " arquivo";
                } else if (files.length == 0) {
                    label.textContent = "Escolha os arquivos";
                } else {
                    label.textContent = "Possui " + files.length + " arquivos";
                }
            });
        });
    } else {
        coluna_causa.style.display = 'none';
    }
}

function criandoHTMLFiles(i) {
    // Criar o contêiner principal 'div'
    var campoArquivos = document.createElement('div');
    campoArquivos.id = "campo_arquivos_" + i;
    campoArquivos.name = "campo_arquivos_" + i;
    campoArquivos.className = 'col-sm-6 mb-4';

    // Criar o 'label' para os arquivos
    var labelArquivos = document.createElement('label');
    labelArquivos.textContent = 'Escolha os arquivos da causa '+i+':';

    // Criar a 'div' customizada para o arquivo
    var customFileDiv = document.createElement('div');
    customFileDiv.className = 'custom-file';

    // Criar o 'input' para selecionar arquivos
    var inputFile = document.createElement('input');
    inputFile.type = 'file';
    inputFile.className = 'custom-file-input';
    inputFile.id = 'foto_inspecao_'+i;
    inputFile.name = 'foto_inspecao_'+i;
    inputFile.accept = 'image/*';
    inputFile.multiple = true;

    // Criar o 'label' para o input de arquivos
    var labelInputFile = document.createElement('label');
    labelInputFile.className = 'custom-file-label';
    labelInputFile.htmlFor = 'foto_inspecao_'+i;
    labelInputFile.textContent = 'Escolha os arquivos';

    // Anexar os elementos na estrutura correta
    customFileDiv.appendChild(inputFile);
    customFileDiv.appendChild(labelInputFile);

    campoArquivos.appendChild(labelArquivos);
    campoArquivos.appendChild(customFileDiv);

    return campoArquivos
}

// Event listener para chamar a função quando o valor de n_nao_conformidades mudar
document.getElementById("n_conformidades").addEventListener("input", function() {
    adicionarSelects("n_nao_conformidades","coluna_causa");
});

document.getElementById("n_conformidades_reinspecao").addEventListener("input", () => {
    adicionarSelects("n_nao_conformidades_reinspecao","coluna_causa_reinspecao");
});