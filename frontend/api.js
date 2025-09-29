// app.js

const API_BASE_URL = 'http://127.0.0.1:8000';

const cepInput = document.getElementById('cep');
const addressSelect = document.getElementById('address-select');
const feedbackDiv = document.getElementById('feedback');
// ADICIONE AS NOVAS REFERÊNCIAS
const loadingSpinner = document.getElementById('loading-spinner');
const searchButton = document.querySelector('button'); // Ou use id="search-button" no HTML

// ===============================================
// FUNÇÕES PARA GERENCIAR O ESTADO DE CARREGAMENTO
// ===============================================
function showLoadingState() {
    loadingSpinner.classList.remove('spinner-hidden');
    searchButton.disabled = true;
    feedbackDiv.textContent = "Carregando...";
}

function hideLoadingState(message = null) {
    loadingSpinner.classList.add('spinner-hidden');
    searchButton.disabled = false;
    if (message) {
        feedbackDiv.textContent = message;
    }
}

// ===============================================
// FUNÇÃO PRINCIPAL DE BUSCA (MODIFICADA)
// ===============================================
async function buscarEnderecos() {
    addressSelect.innerHTML = '<option>Nenhum endereço encontrado</option>';
    addressSelect.disabled = true;
    
    const cep = cepInput.value.replace(/\D/g, '');
    if (cep.length < 8) {
        hideLoadingState("Por favor, digite um CEP válido.");
        return;
    }

    // CHAME A FUNÇÃO PARA MOSTRAR O ESTADO DE CARREGAMENTO
    showLoadingState();

    try {
        const url = `${API_BASE_URL}/api/viabilidade?cep=${cep}`;
        const response = await fetch(url);

        if (!response.ok) {
            if (response.status === 404) {
                hideLoadingState("Nenhum endereço encontrado para este CEP.");
                return;
            }
            throw new Error(`Erro HTTP! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.enderecos && data.enderecos.length > 0) {
            addressSelect.innerHTML = '';
            data.enderecos.forEach(endereco => {
                const option = document.createElement('option');
                option.value = endereco.pn_uso;
                option.textContent = endereco.endereco_completo;
                addressSelect.appendChild(option);
            });
            addressSelect.disabled = false;
            hideLoadingState(`Encontrados ${data.enderecos.length} endereços.`);
        } else {
            hideLoadingState("Nenhum endereço encontrado para este CEP.");
        }

    } catch (error) {
        console.error('Erro na requisição:', error);
        hideLoadingState("Ocorreu um erro ao buscar os dados. Verifique a API.");
    }
}