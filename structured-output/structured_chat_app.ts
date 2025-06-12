// TypeScript for Structured Output Chat App
import { marked } from 'https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js'

const convElement = document.getElementById('conversation')
const promptInput = document.getElementById('prompt-input') as HTMLInputElement
const spinner = document.getElementById('spinner')

// Message interface matching the backend
interface Message {
  role: string
  content: string
  timestamp: string
  message_type: 'text' | 'structured'
  structured_data?: any
}

// Structured data renderers
function renderTaskList(data: any): string {
  const tasks = data.tasks.map((task: any) => `
    <div class="task-item">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h6 class="mb-1">${task.title}</h6>
        <span class="task-priority priority-${task.priority}">${task.priority}</span>
      </div>
      <p class="mb-2 text-muted">${task.description}</p>
      <div class="d-flex justify-content-between small text-muted">
        <span><i class="fas fa-clock"></i> ${task.estimated_time}</span>
        <span><i class="fas fa-tag"></i> ${task.category}</span>
      </div>
    </div>
  `).join('')

  return `
    <div class="structured-data">
      <div class="structured-header">
        <span><i class="fas fa-tasks"></i> Task List</span>
        <span class="badge bg-primary">${data.total_tasks} tasks</span>
      </div>
      <div class="structured-content">
        <p class="mb-3"><strong>Summary:</strong> ${data.summary}</p>
        ${tasks}
      </div>
    </div>
  `
}

function renderRecipe(data: any): string {
  const ingredients = data.ingredients.map((ing: any) => `
    <div class="ingredient-item">
      <span>${ing.name}</span>
      <strong>${ing.amount}</strong>
    </div>
  `).join('')

  const instructions = data.instructions.map((instruction: string, index: number) => `
    <div class="mb-2">
      <span class="badge bg-secondary me-2">${index + 1}</span>
      ${instruction}
    </div>
  `).join('')

  const difficultyColor = {
    easy: 'success',
    medium: 'warning', 
    hard: 'danger'
  }[data.difficulty] || 'secondary'

  return `
    <div class="structured-data">
      <div class="structured-header">
        <span><i class="fas fa-utensils"></i> ${data.name}</span>
        <span class="badge bg-${difficultyColor}">${data.difficulty}</span>
      </div>
      <div class="structured-content">
        <p class="mb-3">${data.description}</p>
        
        <div class="row mb-3">
          <div class="col-sm-3">
            <small class="text-muted">Prep Time</small><br>
            <strong>${data.prep_time}</strong>
          </div>
          <div class="col-sm-3">
            <small class="text-muted">Cook Time</small><br>
            <strong>${data.cook_time}</strong>
          </div>
          <div class="col-sm-3">
            <small class="text-muted">Servings</small><br>
            <strong>${data.servings}</strong>
          </div>
          <div class="col-sm-3">
            <small class="text-muted">Difficulty</small><br>
            <strong>${data.difficulty}</strong>
          </div>
        </div>

        <div class="recipe-section">
          <h6><i class="fas fa-shopping-basket"></i> Ingredients</h6>
          ${ingredients}
        </div>

        <div class="recipe-section">
          <h6><i class="fas fa-list-ol"></i> Instructions</h6>
          ${instructions}
        </div>
      </div>
    </div>
  `
}

function renderWeatherForecast(data: any): string {
  const conditionIcons = {
    sunny: 'fas fa-sun',
    cloudy: 'fas fa-cloud',
    rainy: 'fas fa-cloud-rain',
    snowy: 'fas fa-snowflake',
    stormy: 'fas fa-bolt',
    foggy: 'fas fa-smog'
  }

  const recommendations = data.recommendations.map((rec: string) => `
    <li><i class="fas fa-check-circle"></i> ${rec}</li>
  `).join('')

  return `
    <div class="structured-data">
      <div class="structured-header">
        <span><i class="fas fa-cloud-sun"></i> Weather Forecast</span>
        <span class="badge bg-info">${data.location}</span>
      </div>
      <div class="structured-content">
        <div class="weather-card">
          <div class="weather-main">
            <div>
              <h3 class="mb-0">${data.temperature}</h3>
              <p class="mb-0">${data.location}</p>
            </div>
            <div class="text-center">
              <i class="${conditionIcons[data.current_condition] || 'fas fa-question'} fa-3x"></i>
              <p class="mb-0 mt-2">${data.current_condition}</p>
            </div>
          </div>
          
          <div class="row text-center">
            <div class="col-6">
              <i class="fas fa-tint"></i> Humidity<br>
              <strong>${data.humidity}</strong>
            </div>
            <div class="col-6">
              <i class="fas fa-wind"></i> Wind<br>
              <strong>${data.wind_speed}</strong>
            </div>
          </div>
        </div>
        
        <div class="mt-3">
          <p><strong>Forecast:</strong> ${data.forecast_summary}</p>
          <h6><i class="fas fa-lightbulb"></i> Recommendations:</h6>
          <ul class="list-unstyled">
            ${recommendations}
          </ul>
        </div>
      </div>
    </div>
  `
}

function renderProductReview(data: any): string {
  const stars = '★'.repeat(data.rating) + '☆'.repeat(5 - data.rating)
  
  const pros = data.pros.map((pro: string) => `
    <li class="text-success"><i class="fas fa-plus-circle"></i> ${pro}</li>
  `).join('')

  const cons = data.cons.map((con: string) => `
    <li class="text-danger"><i class="fas fa-minus-circle"></i> ${con}</li>
  `).join('')

  const recommendBadge = data.recommendation ? 
    '<span class="badge bg-success">Recommended</span>' : 
    '<span class="badge bg-warning">Not Recommended</span>'

  return `
    <div class="structured-data">
      <div class="structured-header">
        <span><i class="fas fa-star"></i> Product Review</span>
        ${recommendBadge}
      </div>
      <div class="structured-content">
        <h5>${data.product_name}</h5>
        <div class="mb-3">
          <span class="rating-stars">${stars}</span>
          <strong>${data.rating}/5 stars</strong>
        </div>
        
        <p class="mb-3">${data.summary}</p>
        
        <div class="row">
          <div class="col-md-6">
            <h6 class="text-success"><i class="fas fa-thumbs-up"></i> Pros</h6>
            <ul class="list-unstyled">
              ${pros}
            </ul>
          </div>
          <div class="col-md-6">
            <h6 class="text-danger"><i class="fas fa-thumbs-down"></i> Cons</h6>
            <ul class="list-unstyled">
              ${cons}
            </ul>
          </div>
        </div>
      </div>
    </div>
  `
}

function renderStructuredData(data: any, messageType: string): string {
  // Try to detect the type of structured data
  if (data.tasks && data.total_tasks !== undefined) {
    return renderTaskList(data)
  } else if (data.ingredients && data.instructions) {
    return renderRecipe(data)
  } else if (data.current_condition && data.temperature) {
    return renderWeatherForecast(data)
  } else if (data.rating && data.pros && data.cons) {
    return renderProductReview(data)
  } else {
    // Fallback to JSON display
    return `
      <div class="structured-data">
        <div class="structured-header">
          <span><i class="fas fa-code"></i> Structured Data</span>
        </div>
        <div class="structured-content">
          <pre class="bg-light p-3 rounded"><code>${JSON.stringify(data, null, 2)}</code></pre>
        </div>
      </div>
    `
  }
}

// Stream response handler
async function onFetchResponse(response: Response): Promise<void> {
  let text = ''
  let decoder = new TextDecoder()
  
  if (response.ok) {
    const reader = response.body.getReader()
    while (true) {
      const {done, value} = await reader.read()
      if (done) break
      
      text += decoder.decode(value)
      addMessages(text)
      spinner.classList.remove('active')
    }
    addMessages(text)
    promptInput.disabled = false
    promptInput.focus()
  } else {
    const text = await response.text()
    console.error(`Unexpected response: ${response.status}`, {response, text})
    throw new Error(`Unexpected response: ${response.status}`)
  }
}

function addMessages(responseText: string) {
  const lines = responseText.split('\n')
  const messages: Message[] = lines
    .filter(line => line.length > 1)
    .map(j => JSON.parse(j))
  
  for (const message of messages) {
    const {timestamp, role, content, message_type, structured_data} = message
    const id = `msg-${timestamp}`
    let msgDiv = document.getElementById(id)
    
    if (!msgDiv) {
      msgDiv = document.createElement('div')
      msgDiv.id = id
      msgDiv.title = `${role} at ${timestamp}`
      msgDiv.classList.add('border-bottom', 'pb-3', 'mb-3', role)
      convElement.appendChild(msgDiv)
    }
    
    let messageContent = marked.parse(content)
    
    // Add structured data if present
    if (message_type === 'structured' && structured_data) {
      messageContent += renderStructuredData(structured_data, message_type)
    }
    
    msgDiv.innerHTML = messageContent
  }
  
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

function onError(error: any) {
  console.error(error)
  document.getElementById('error').classList.remove('d-none')
  document.getElementById('spinner').classList.remove('active')
}

async function onSubmit(e: SubmitEvent): Promise<void> {
  e.preventDefault()
  spinner.classList.add('active')
  const body = new FormData(e.target as HTMLFormElement)

  promptInput.value = ''
  promptInput.disabled = true

  const response = await fetch('/chat/', {method: 'POST', body})
  await onFetchResponse(response)
}

// Event listeners
document.querySelector('form').addEventListener('submit', (e) => onSubmit(e).catch(onError))

// Example query click handlers
document.querySelectorAll('.example-query').forEach(element => {
  element.addEventListener('click', (e) => {
    const query = (e.target as HTMLElement).dataset.query
    if (query) {
      promptInput.value = query
      promptInput.focus()
    }
  })
})

// Load existing messages on page load
fetch('/chat/').then(onFetchResponse).catch(onError) 