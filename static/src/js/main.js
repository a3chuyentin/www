import '../css/tailwind.css';

import '../css/components.css';

import './init.js';

import EasyMDE from 'easymde';
import hljs from 'highlight.js';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true,
    mangle: false,
    headerIds: false
});

window.marked = marked;
window.DOMPurify = DOMPurify;

window.renderMathJax = function() {
    if (window.MathJax) {
    }
};

const observer = new MutationObserver(function() {
    window.renderMathJax();
});

observer.observe(document.body, { childList: true, subtree: true });

if (window.MathJax) {
    window.MathJax.typesetPromise();
}