// Limpieza: Eliminadas variables globales sin uso (savedpasttext, savedpastresponse)

const messagesContainer = document.getElementById('messages-container');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');

const addMessage = (message, role, imgSrc) => {
  const messageElement = document.createElement('div');
  const textElement = document.createElement('p');
  messageElement.className = `message ${role}`;
  
  const imgElement = document.createElement('img');
  imgElement.src = imgSrc;
  
  messageElement.appendChild(imgElement);
  textElement.innerText = message;
  messageElement.appendChild(textElement);
  messagesContainer.appendChild(messageElement);
  
  const clearDiv = document.createElement("div");
  clearDiv.style.clear = "both";
  messagesContainer.appendChild(clearDiv);

  messagesContainer.scrollTop = messagesContainer.scrollHeight;
};

const sendMessage = async (message) => {
  // Deshabilitar entrada mientras el bot responde para evitar envíos dobles
  messageInput.disabled = true;

  addMessage(message, 'user', '/static/images/user.png');
  
  const loadingElement = document.createElement('div');
  const loadingtextElement = document.createElement('p');
  loadingElement.className = `loading-animation`;
  loadingtextElement.className = `loading-text`;
  loadingtextElement.innerText = 'Cargando... Por favor espera';
  messagesContainer.appendChild(loadingElement);
  messagesContainer.appendChild(loadingtextElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  async function makePostRequest(msg) {
    const url = 'http://localhost:5000/chatbot';
    const requestBody = { prompt: msg, message: msg };
  
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
  
      if (!response.ok) {
        throw new Error(`Servidor respondió con código ${response.status}`);
      }

      const data = await response.json();
      const botText = data.response || data.reply || data.error || "Sin respuesta recibida";
      
      return { success: true, text: botText };
    } catch (error) {
      console.error('Error en fetch:', error);
      return { success: false, text: error.message };
    }
  }
  
  const result = await makePostRequest(message);
  
  const loadanimation = document.querySelector('.loading-animation');
  const loadtxt = document.querySelector('.loading-text');
  if (loadanimation) loadanimation.remove();
  if (loadtxt) loadtxt.remove();

  if (!result.success) {
    addMessage(`Error: ${result.text}`, 'error', '/static/images/Error.png');
  } else {
    addMessage(result.text, 'aibot', '/static/images/Bot_logos.png');
  }

  // Volver a habilitar la entrada y enfocar
  messageInput.disabled = false;
  messageInput.focus();
};

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (message !== '') {
    messageInput.value = '';
    await sendMessage(message);
  }
});

messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    messageForm.dispatchEvent(new Event('submit'));
  }
});





