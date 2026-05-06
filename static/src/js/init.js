import EasyMDE from 'easymde';
import hljs from 'highlight.js';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

let currentPage = 2;
let isLoading = false;
let currentFilter = 'all';
let currentSearch = '';

window.EasyMDE = EasyMDE;
window.marked = marked;
window.DOMPurify = DOMPurify;

function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    if (token) return token.content;
    const cookie = document.cookie.match(/csrftoken=([^;]+)/);
    return cookie ? cookie[1] : '';
}

function renderMathJax() {
    if (window.MathJax) {
        MathJax.typesetPromise().catch(err => console.log('MathJax error:', err));
    }
}

marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true
});

const purifyConfig = {
    ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'del', 'ins', 'mark',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'code', 'pre', 'blockquote',
        'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'div', 'span', 'hr', 'details', 'summary'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'target', 'rel', 'class'],
    ALLOW_DATA_ATTR: false,
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'button'],
    FORBID_ATTR: ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur'],
    ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tp?s?|mailto|tel):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
};

function initMarkdownEditors() {
    const textareas = document.querySelectorAll('#markdown-editor, [data-editor="true"]');
    
    textareas.forEach(function(textarea) {
        if (textarea.easymdeInstance) return;
        textarea.removeAttribute('required');
        
        try {
            const easyMDE = new EasyMDE({
                element: textarea,
                spellChecker: false,
                placeholder: 'Viết nội dung bằng Markdown...',
                toolbar: [
                    'bold', 'italic', 'heading', '|',
                    'code', 'quote', '|',
                    'unordered-list', 'ordered-list', '|',
                    'link', 'image', 'table', '|',
                    'preview', 'side-by-side', 'fullscreen', '|',
                    'guide'
                ],
                renderingConfig: {
                    codeSyntaxHighlighting: true,
                    hljs: hljs
                },
                previewRender: function(plainText, preview) {
                    let sanitizedText = plainText;
                    sanitizedText = sanitizedText.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
                    sanitizedText = sanitizedText.replace(/javascript\s*:/gi, '');
                    sanitizedText = sanitizedText.replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '');
                    
                    let html = marked.parse(sanitizedText);
                    html = DOMPurify.sanitize(html, purifyConfig);
                    
                    if (preview) {
                        preview.innerHTML = html;
                        setTimeout(() => renderMathJax(), 100);
                    }
                    
                    return html;
                },
                blockStyles: { bold: "**", italic: "*", code: "`" },
                shortcuts: { drawTable: "Cmd-Alt-T" }
            });
            
            textarea.easymdeInstance = easyMDE;
        } catch (error) {
            console.error('Failed to initialize editor:', error);
        }
    });
}

function initSyntaxHighlighting() {
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

async function loadMorePosts() {
    if (isLoading) return;
    
    isLoading = true;
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    
    let url = `/posts/api/load-more/?page=${currentPage}&filter=${currentFilter}`;
    if (currentSearch) {
        url += `&q=${encodeURIComponent(currentSearch)}`;
    }
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.html && data.html.trim()) {
            const container = document.getElementById('posts-container');
            if (container) {
                container.insertAdjacentHTML('beforeend', data.html);
                currentPage = data.page;
                renderMathJax();
                initSyntaxHighlighting();
            }
        }
    } catch (error) {
        console.error('Error loading more posts:', error);
    } finally {
        isLoading = false;
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

function initInfiniteScroll() {
    const container = document.getElementById('posts-container');
    if (!container) return;
    
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.dataset.filter;
            const url = new URL(window.location.href);
            url.searchParams.set('filter', filter);
            window.location.href = url.toString();
        });
    });
    
    currentFilter = container.dataset.filter || 'all';
    currentSearch = container.dataset.search || '';
    
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const scrollPosition = window.innerHeight + window.scrollY;
            const threshold = document.body.scrollHeight - 800;
            
            if (scrollPosition >= threshold && !isLoading) {
                loadMorePosts();
            }
        }, 200);
    });
}

async function handleVote(voteBtn) {
    const url = voteBtn.dataset.url;
    const value = parseInt(voteBtn.dataset.value);
    
    if (!url) return;
    
    const isCommentVote = voteBtn.classList.contains('upvote-comment') || voteBtn.classList.contains('downvote-comment');
    
    let voteCountSpan;
    if (isCommentVote) {
        const commentId = voteBtn.dataset.commentId;
        voteCountSpan = document.getElementById('comment-vote-count-' + commentId);
    } else {
        const postCard = voteBtn.closest('article');
        voteCountSpan = postCard ? postCard.querySelector('.vote-count-up') : document.getElementById('vote-count');
    }
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'value=' + value
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (voteCountSpan) {
                voteCountSpan.textContent = data.total_votes;
            }
            
            const container = voteBtn.closest('.vote-container') || voteBtn.parentElement;
            if (container) {
                const upBtn = container.querySelector('.vote-up, .upvote-comment');
                const downBtn = container.querySelector('.vote-down, .downvote-comment');
                
                if (upBtn) upBtn.classList.remove('active');
                if (downBtn) downBtn.classList.remove('active');
                
                if (data.user_vote === 1 && upBtn) {
                    upBtn.classList.add('active');
                } else if (data.user_vote === -1 && downBtn) {
                    downBtn.classList.add('active');
                }
            }
        }
    } catch (error) {
        console.error('Vote error:', error);
    }
}

function initVoteButtons() {
    document.addEventListener('click', async function(e) {
        const voteBtn = e.target.closest('.vote-btn, .comment-vote-btn');
        if (voteBtn) {
            e.preventDefault();
            await handleVote(voteBtn);
        }
    });
}

function initReplyButtons() {
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            const formContainer = document.getElementById('reply-form-' + commentId);
            if (formContainer) {
                formContainer.classList.toggle('hidden');
            }
        });
    });
    
    document.querySelectorAll('.cancel-reply').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.reply-form').classList.add('hidden');
        });
    });
}

function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea[data-editor="true"], #markdown-editor');
            if (textarea && textarea.easymdeInstance) {
                const content = textarea.easymdeInstance.value();
                if (!content.trim()) {
                    e.preventDefault();
                    alert('Vui lòng nhập nội dung trước khi gửi.');
                    return false;
                }
            }
        });
    });
}

function initCommentActions() {
    document.querySelectorAll('.edit-comment-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            const editForm = document.getElementById('edit-form-' + commentId);
            const content = document.getElementById('comment-content-' + commentId);
            if (editForm) {
                editForm.classList.toggle('hidden');
                if (content) content.classList.toggle('hidden');
            }
        });
    });
    
    document.querySelectorAll('.cancel-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const editForm = document.getElementById('edit-form-' + commentId);
            const content = document.getElementById('comment-content-' + commentId);
            if (editForm) editForm.classList.add('hidden');
            if (content) content.classList.remove('hidden');
        });
    });
    
    document.querySelectorAll('.edit-comment-form form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const url = this.dataset.editUrl;
            const textarea = this.querySelector('textarea');
            const content = textarea.value;
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'content=' + encodeURIComponent(content)
                });
                
                if (response.ok) {
                    location.reload();
                }
            } catch (error) {
                console.error('Edit error:', error);
            }
        });
    });
    
    document.querySelectorAll('.delete-comment-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (!confirm('Bạn có chắc muốn xóa bình luận này?')) return;
            
            const url = this.dataset.deleteUrl;
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                    }
                });
                
                if (response.ok) {
                    location.reload();
                }
            } catch (error) {
                console.error('Delete error:', error);
            }
        });
    });
}

function initPasswordValidation() {
    const passwordInput = document.getElementById('password1');
    const confirmInput = document.getElementById('password2');
    const matchMessage = document.getElementById('match-message');
    
    if (!passwordInput) return;
    
    function updateCheck(checkName, passed) {
        const el = document.querySelector(`[data-check="${checkName}"]`);
        if (!el) return;
        const icon = el.querySelector('i');
        const span = el.querySelector('span');
        
        if (passed) {
            icon.className = 'fas fa-check-circle text-green-500';
            span.className = 'text-green-600';
        } else {
            icon.className = 'fas fa-circle text-[6px] text-surface-300';
            span.className = 'text-surface-400';
        }
    }
    
    function getPasswordStrength(password) {
        let score = 0;
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        return score;
    }
    
    function checkMatch() {
        if (!confirmInput) return;
        const password = passwordInput.value;
        const confirm = confirmInput.value;
        
        if (confirm.length === 0) {
            matchMessage.classList.add('hidden');
        } else if (password === confirm) {
            matchMessage.textContent = '✓ Mật khẩu khớp';
            matchMessage.className = 'text-xs mt-1 text-green-500';
            matchMessage.classList.remove('hidden');
        } else {
            matchMessage.textContent = '✗ Mật khẩu không khớp';
            matchMessage.className = 'text-xs mt-1 text-red-500';
            matchMessage.classList.remove('hidden');
        }
    }
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const username = document.querySelector('input[name="username"]')?.value || '';
        const email = document.querySelector('input[name="email"]')?.value || '';
        const fullName = document.querySelector('input[name="full_name"]')?.value || '';
        
        updateCheck('length', password.length >= 8);
        
        const isNumericOnly = /^\d+$/.test(password);
        updateCheck('numeric', password.length > 0 && !isNumericOnly);
        
        let similar = false;
        if (password.length >= 3) {
            const lowerPass = password.toLowerCase();
            [username, email.split('@')[0], ...fullName.split(' ')].forEach(word => {
                if (word && word.length >= 3 && lowerPass.includes(word.toLowerCase())) {
                    similar = true;
                }
            });
        }
        updateCheck('similar', password.length > 0 && !similar);
        
        const strength = getPasswordStrength(password);
        const strengthText = document.getElementById('strength-text');
        const strengthCheck = document.querySelector('[data-check="strength"]');
        const strengthIcon = strengthCheck?.querySelector('i');
        
        if (password.length === 0) {
            strengthText.textContent = 'Nhập mật khẩu';
            strengthText.className = 'font-semibold text-surface-400';
            if (strengthIcon) strengthIcon.className = 'fas fa-circle text-[6px] text-surface-300';
        } else if (strength <= 2) {
            strengthText.textContent = 'Yếu';
            strengthText.className = 'font-semibold text-red-500';
            if (strengthIcon) strengthIcon.className = 'fas fa-times-circle text-red-500';
        } else if (strength <= 4) {
            strengthText.textContent = 'Trung bình';
            strengthText.className = 'font-semibold text-yellow-500';
            if (strengthIcon) strengthIcon.className = 'fas fa-exclamation-circle text-yellow-500';
        } else {
            strengthText.textContent = 'Mạnh';
            strengthText.className = 'font-semibold text-green-500';
            if (strengthIcon) strengthIcon.className = 'fas fa-check-circle text-green-500';
        }
        
        checkMatch();
    });
    
    if (confirmInput) {
        confirmInput.addEventListener('input', checkMatch);
    }
}

function init() {
    initMarkdownEditors();
    initSyntaxHighlighting();
    initVoteButtons();
    initReplyButtons();
    initCommentActions();
    initFormValidation();
    initInfiniteScroll();
    initPasswordValidation();
    
    setTimeout(() => renderMathJax(), 500);
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                initSyntaxHighlighting();
                renderMathJax();
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

document.addEventListener('DOMContentLoaded', init);

export { initMarkdownEditors, initSyntaxHighlighting, renderMathJax, loadMorePosts };