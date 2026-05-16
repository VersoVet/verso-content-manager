"""Dashboard HTML template for verso-content-manager."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>verso-content-manager — Gestion Articles WordPress</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1200px;
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            padding: 40px;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                gap: 30px;
                padding: 20px;
            }
        }

        h1 {
            grid-column: 1 / -1;
            color: #1c2445;
            margin-bottom: 30px;
            font-size: 28px;
        }

        .section-title {
            color: #1c2445;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .template-buttons {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }

        .template-btn {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            text-align: left;
            transition: all 0.3s;
            font-size: 14px;
        }

        .template-btn:hover {
            background: #f5f5f5;
            border-color: #667eea;
        }

        .template-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-family: "Monaco", "Menlo", monospace;
            font-size: 12px;
            resize: vertical;
        }

        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s;
        }

        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .action-buttons button {
            flex: 1;
        }

        .articles-list {
            max-height: 500px;
            overflow-y: auto;
        }

        .article-item {
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }

        .article-info {
            flex: 1;
        }

        .article-id {
            font-weight: 600;
            color: #1c2445;
            font-size: 14px;
        }

        .article-title {
            color: #666;
            font-size: 13px;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .article-status {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }

        .article-status.publish {
            background: #4caf50;
            color: white;
        }

        .article-status.draft {
            background: #ff9800;
            color: white;
        }

        .article-actions {
            display: flex;
            gap: 5px;
        }

        .article-actions button {
            padding: 6px 12px;
            font-size: 12px;
        }

        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }

        .result.success {
            background: #c8e6c9;
            color: #2e7d32;
            border: 1px solid #a5d6a7;
            display: block;
        }

        .result.error {
            background: #ffcdd2;
            color: #c62828;
            border: 1px solid #ef9a9a;
            display: block;
        }

        .loading {
            display: none;
            text-align: center;
            color: #667eea;
        }

        .loading.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 verso-content-manager — Gestion Articles</h1>

        <!-- Créer Article -->
        <div>
            <div class="section-title">🎨 Créer Article</div>

            <div class="section-title" style="font-size: 14px; font-weight: 500; margin: 15px 0 10px 0;">
                Templates:
            </div>
            <div class="template-buttons">
                <button class="template-btn active" data-template="presse">📰 Article de Presse</button>
                <button class="template-btn" data-template="pathologie">🏥 Pathologie Animale</button>
                <button class="template-btn" data-template="outil">🔧 Outil/Équipement</button>
                <button class="template-btn" data-template="libre">📋 JSON Libre</button>
            </div>

            <textarea id="jsonInput" placeholder="Coller ou modifier JSON ici...">{"title":"","status":"draft","blocks":[]}</textarea>

            <div class="action-buttons">
                <button onclick="createArticle()">🚀 Créer</button>
                <button onclick="loadJsonFile()">📁 Upload JSON</button>
            </div>

            <div id="createResult" class="result"></div>
            <div id="createLoading" class="loading">⏳ Création en cours...</div>
        </div>

        <!-- Articles Existants -->
        <div>
            <div class="section-title">📋 Articles Existants</div>

            <div class="section-title" style="font-size: 14px; font-weight: 500; margin: 15px 0 10px 0;">
                Filtrer:
            </div>
            <div class="action-buttons">
                <button style="background: #4caf50;" onclick="loadArticles('publish')">✓ Publié</button>
                <button style="background: #ff9800;" onclick="loadArticles('draft')">✏️ Brouillon</button>
                <button style="background: #2196f3;" onclick="loadArticles('all')">🔄 Tout</button>
            </div>

            <div id="articlesList" class="articles-list">
                <p style="color: #999; text-align: center; padding: 20px;">Chargement...</p>
            </div>

            <div id="listLoading" class="loading">⏳ Chargement...</div>
        </div>
    </div>

    <input type="file" id="jsonFile" accept=".json" style="display: none;">

    <script>
        const API_BASE = '/articles';
        const TEMPLATES_BASE = '/templates';

        async function loadTemplate(name) {
            if (name === 'libre') return;
            try {
                const response = await fetch(`${TEMPLATES_BASE}/${name}`);
                const template = await response.json();
                document.getElementById('jsonInput').value = JSON.stringify(template, null, 2);
            } catch (error) {
                console.error('Failed to load template:', error);
            }
        }

        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.template-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                loadTemplate(this.dataset.template);
            });
        });

        async function createArticle() {
            const resultDiv = document.getElementById('createResult');
            const loadingDiv = document.getElementById('createLoading');
            resultDiv.style.display = 'none';
            loadingDiv.classList.add('active');

            try {
                const jsonText = document.getElementById('jsonInput').value.trim();
                const articleData = JSON.parse(jsonText);

                const response = await fetch(API_BASE, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(articleData)
                });

                const result = await response.json();
                loadingDiv.classList.remove('active');

                if (!response.ok) {
                    showResult('error', `Erreur: ${result.detail || response.statusText}`);
                    return;
                }

                showResult('success', `✓ Article créé! ID: ${result.id}<br><a href="${result.link}" target="_blank">Voir sur le site →</a>`);
                loadArticles('all');
            } catch (error) {
                loadingDiv.classList.remove('active');
                showResult('error', `Erreur: ${error.message}`);
            }
        }

        async function loadArticles(status) {
            const listDiv = document.getElementById('articlesList');
            const loadingDiv = document.getElementById('listLoading');
            listDiv.innerHTML = '';
            loadingDiv.classList.add('active');

            try {
                const params = status === 'all' ? '' : `?status=${status}`;
                const response = await fetch(`${API_BASE}${params}`);
                const articles = await response.json();
                loadingDiv.classList.remove('active');

                if (!Array.isArray(articles) || articles.length === 0) {
                    listDiv.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Aucun article</p>';
                    return;
                }

                articles.forEach(article => {
                    const statusClass = article.status === 'publish' ? 'publish' : 'draft';
                    const item = document.createElement('div');
                    item.className = 'article-item';
                    item.innerHTML = `
                        <div class="article-info">
                            <div class="article-id">#${article.id}</div>
                            <div class="article-title">${article.title || 'Sans titre'}</div>
                            <span class="article-status ${statusClass}">${article.status === 'publish' ? '✓ Publié' : '✏️ Brouillon'}</span>
                        </div>
                        <div class="article-actions">
                            <button onclick="editArticle(${article.id})">✏️</button>
                            ${article.status === 'draft' ? `<button onclick="publishArticle(${article.id})">📤</button>` : ''}
                            <button onclick="deleteArticle(${article.id})">🗑️</button>
                        </div>
                    `;
                    listDiv.appendChild(item);
                });
            } catch (error) {
                loadingDiv.classList.remove('active');
                listDiv.innerHTML = `<p style="color: #c62828; padding: 20px;">Erreur: ${error.message}</p>`;
            }
        }

        async function publishArticle(id) {
            if (!confirm('Publier cet article?')) return;
            try {
                await fetch(`${API_BASE}/${id}/publish`, { method: 'POST' });
                loadArticles('all');
            } catch (error) {
                alert(`Erreur: ${error.message}`);
            }
        }

        async function deleteArticle(id) {
            if (!confirm('Supprimer cet article?')) return;
            try {
                await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
                loadArticles('all');
            } catch (error) {
                alert(`Erreur: ${error.message}`);
            }
        }

        function editArticle(id) {
            alert('Édition directe via le dashboard: à implémenter');
        }

        function loadJsonFile() {
            const input = document.getElementById('jsonFile');
            input.click();
            input.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('jsonInput').value = e.target.result;
                };
                reader.readAsText(file);
            });
        }

        function showResult(type, message) {
            const resultDiv = document.getElementById('createResult');
            resultDiv.className = `result ${type}`;
            resultDiv.innerHTML = message;
        }

        // Load articles on page load
        window.addEventListener('load', () => loadArticles('all'));
    </script>
</body>
</html>
"""
