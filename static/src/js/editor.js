import EasyMDE from 'easymde';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

let currentEditor = null;

document.addEventListener('DOMContentLoaded', function() {
  const editorElement = document.getElementById('markdown-editor');
  if (editorElement) {
    currentEditor = new EasyMDE({
      element: editorElement,
      spellChecker: false,
      toolbar: [
        'bold', 'italic', 'heading', '|',
        'code', 'quote', '|',
        'unordered-list', 'ordered-list', '|',
        'link', 'image', 'table', '|',
        'preview', 'guide', 'fullscreen'
      ],
      placeholder: 'Viết nội dung bằng Markdown...',
      renderingConfig: {
        codeSyntaxHighlighting: true
      },
      previewRender: function(plainText) {
        const html = marked.parse(plainText);
        return DOMPurify.sanitize(html, {
          ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                         'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'a', 'img', 'table', 
                         'thead', 'tbody', 'tr', 'th', 'td', 'div', 'span'],
          ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id']
        });
      }
    });
  }
  
  window.copyMarkdown = function() {
    if (currentEditor) {
      const content = currentEditor.value();
      navigator.clipboard.writeText(content);
      showNotification('Đã copy nội dung Markdown!', 'success');
    }
  };
  
  window.copyHTML = function() {
    if (currentEditor) {
      const content = currentEditor.value();
      const html = marked.parse(content);
      const cleanHtml = DOMPurify.sanitize(html);
      navigator.clipboard.writeText(cleanHtml);
      showNotification('Đã copy HTML!', 'success');
    }
  };
});

function showNotification(message, type) {
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background-color: ${type === 'success' ? '#4caf50' : '#f44336'};
    color: white;
    border-radius: 4px;
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
`;
document.head.appendChild(style);