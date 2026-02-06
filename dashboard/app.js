const DATA_URL = '../data/articles.json';
const STATE_KEY = 'ai_pulse_saved';

class App {
    constructor() {
        this.articles = [];
        this.savedIds = new Set(JSON.parse(localStorage.getItem(STATE_KEY)) || []);
        this.currentFilter = 'all';
        this.init();
    }

    async init() {
        this.bindEvents();
        this.updateSavedCount();
        await this.fetchData();
    }

    bindEvents() {
        document.querySelector('nav').addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-btn')) {
                this.switchFilter(e.target.dataset.filter);
            }
        });
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData());
    }

    async fetchData() {
        this.showLoading();
        try {
            const res = await fetch(`${DATA_URL}?t=${Date.now()}`);
            if (!res.ok) throw new Error('Network error');
            this.articles = await res.json();
            this.articles.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
            this.render();
        } catch (err) {
            console.error(err);
            document.getElementById('content-area').innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-triangle-exclamation" style="font-size:2rem;margin-bottom:16px;"></i>
                    <p>Failed to load feed. Check if scrapers ran.</p>
                </div>`;
        }
    }

    render() {
        const container = document.getElementById('content-area');
        container.innerHTML = '';

        let items = this.articles;
        if (this.currentFilter === 'saved') {
            items = this.articles.filter(a => this.savedIds.has(a.id));
        } else if (this.currentFilter !== 'all') {
            items = this.articles.filter(a => a.source === this.currentFilter);
        }

        if (!items.length) {
            container.innerHTML = `<div class="empty-state"><p>No articles found.</p></div>`;
            return;
        }

        items.forEach(article => container.appendChild(this.createCard(article)));

        // Update active tab
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === this.currentFilter);
        });
    }

    createCard(article) {
        const isSaved = this.savedIds.has(article.id);
        const date = new Date(article.published_at).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        // ALWAYS show placeholder if no valid image
        const hasImage = article.image_url && article.image_url.startsWith('http');

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-image-container">
                ${hasImage
                ? `<img src="${article.image_url}" alt="" class="card-image" onerror="this.remove();">`
                : `<i class="fa-solid fa-robot"></i>`}
            </div>
            <div class="card-content">
                <div class="card-meta">
                    <span class="source-tag">${article.source}</span>
                    <span>${date}</span>
                </div>
                <a href="${article.url}" target="_blank" class="card-title">${article.title}</a>
                <p class="card-summary">${article.summary || 'No summary.'}</p>
            </div>
            <div class="card-actions">
                <a href="${article.url}" target="_blank" class="read-link">
                    Read Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
                <button class="save-btn ${isSaved ? 'saved' : ''}" data-id="${article.id}">
                    <i class="fa-${isSaved ? 'solid' : 'regular'} fa-bookmark"></i>
                </button>
            </div>
        `;

        card.querySelector('.save-btn').addEventListener('click', (e) => {
            this.toggleSave(article.id, e.currentTarget);
        });

        return card;
    }

    toggleSave(id, btn) {
        if (this.savedIds.has(id)) {
            this.savedIds.delete(id);
            btn.classList.remove('saved');
            btn.querySelector('i').className = 'fa-regular fa-bookmark';
            this.showToast('Removed');
        } else {
            this.savedIds.add(id);
            btn.classList.add('saved');
            btn.querySelector('i').className = 'fa-solid fa-bookmark';
            this.showToast('Saved!');
        }
        localStorage.setItem(STATE_KEY, JSON.stringify([...this.savedIds]));
        this.updateSavedCount();
        if (this.currentFilter === 'saved') this.render();
    }

    updateSavedCount() {
        document.getElementById('saved-count').textContent = this.savedIds.size;
    }

    switchFilter(filter) {
        if (this.currentFilter === filter) return;
        this.currentFilter = filter;
        this.render();
    }

    async refreshData() {
        await this.fetchData();
        this.showToast('Refreshed!');
    }

    showLoading() {
        document.getElementById('content-area').innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>`;
    }

    showToast(msg) {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
    }
}

document.addEventListener('DOMContentLoaded', () => new App());
