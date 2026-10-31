/**
 * API Utility for Friday Student Productivity & Multimodal Suite
 * Base URL configured to local Python backend at http://127.0.0.1:8080
 */

export const API_BASE = 'http://127.0.0.1:8080';

/**
 * Dispatches a conversational AI query to the backend chat endpoint.
 * Supports text, multimodal vision payloads, and student task types.
 *
 * @param {string} prompt - User message or prompt
 * @param {object} [options] - { conversationId, useRag, modality, imageBase64, taskType }
 * @returns {Promise<{reply: string, status: string, conversationId: string}>}
 */
export async function sendChatMessage(prompt, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 25000);

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt.trim(),
        conversation_id: options.conversationId || undefined,
        use_rag: options.useRag ?? false,
        modality: options.modality || (options.imageBase64 ? 'image' : 'text'),
        image_base64: options.imageBase64 || undefined,
        task_type: options.taskType || undefined,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errText || response.statusText}`);
    }

    const data = await response.json();
    const replyText = data.reply || data.response;

    if (!replyText) {
      throw new Error('Neural core returned an empty response.');
    }

    return {
      reply: replyText,
      status: data.status || 'success',
      conversationId: data.conversation_id,
      citations: data.citations || [],
    };
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Connection to Friday neural core timed out.');
    }
    throw err;
  }
}

/**
 * Dispatches a Chrome automation directive to the local Python bridge.
 */
export async function sendChromeCommand({ command, action, query, url }) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(`${API_BASE}/api/chrome`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: command || undefined,
        action: action || undefined,
        query: query || undefined,
        url: url || undefined,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errText || response.statusText}`);
    }

    const data = await response.json();
    return {
      success: data.success ?? true,
      action: data.action || action,
      message: data.message || `Executed ${action} in Chrome.`,
      details: data.details || {},
    };
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Chrome automation bridge timed out.');
    }
    throw err;
  }
}

/**
 * Uploads a document (PDF, DOCX, TXT) to the RAG knowledge ingestion pipeline.
 */
export async function uploadKnowledgeDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Document upload failed: ${err}`);
  }

  return await response.json();
}

/**
 * Fetches student productivity analytics, active streak, and subject breakdown.
 */
export async function fetchStudyAnalytics() {
  const response = await fetch(`${API_BASE}/api/study/analytics`);
  if (!response.ok) {
    throw new Error('Failed to load study analytics');
  }
  return await response.json();
}

/**
 * Logs a completed study session or Pomodoro interval.
 */
export async function logStudySession({ subject, topic, durationMinutes, notes }) {
  const response = await fetch(`${API_BASE}/api/study/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      subject,
      topic,
      duration_minutes: durationMinutes,
      notes: notes || '',
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to log study session');
  }
  return await response.json();
}

/**
 * Generates an academic PDF study guide or cheat sheet.
 */
export async function generateStudyPDF({
  title,
  subject = 'General Studies',
  documentType = 'study_guide',
  keyTakeaways,
  sections,
  practiceQuestions,
  rawMarkdown,
}) {
  const response = await fetch(`${API_BASE}/api/study/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title,
      subject,
      document_type: documentType,
      key_takeaways: keyTakeaways,
      sections,
      practice_questions: practiceQuestions,
      raw_markdown: rawMarkdown,
    }),
  });

  if (!response.ok) {
    throw new Error('PDF compilation failed.');
  }

  return await response.json();
}
