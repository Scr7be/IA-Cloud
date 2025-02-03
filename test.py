from flask import Flask, render_template, request, redirect, url_for
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'documents'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Créer le dossier documents s'il n'existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Base de documents pour la recherche
documents = {
    "document1": '''The release of DeepSeek R1 stunned Wall Street and Silicon Valley this month, spooking investors and impressing tech leaders. But amid all the talk, many overlooked a critical detail about the way the new Chinese AI model functions—a nuance that has researchers worried about humanity's ability to control sophisticated new artificial intelligence systems.

It's all down to an innovation in how DeepSeek R1 was trained—one that led to surprising behaviors in an early version of the model, which researchers described in the technical documentation accompanying its release.

During testing, researchers noticed that the model would spontaneously switch between English and Chinese while it was solving problems. When they forced it to stick to one language, thus making it easier for users to follow along, they found that the system's ability to solve the same problems would diminish.

That finding rang alarm bells for some AI safety researchers. Currently, the most capable AI systems "think" in human-legible languages, writing out their reasoning before coming to a conclusion. That has been a boon for safety teams, whose most effective guardrails involve monitoring models' so-called "chains of thought" for signs of dangerous behaviors. But DeepSeek's results raised the possibility of a decoupling on the horizon: one where new AI capabilities could be gained from freeing models of the constraints of human language altogether.

To be sure, DeepSeek's language switching is not by itself cause for alarm. Instead, what worries researchers is the new innovation that caused it. The DeepSeek paper describes a novel training method whereby the model was rewarded purely for getting correct answers, regardless of how comprehensible its thinking process was to humans. The worry is that this incentive-based approach could eventually lead AI systems to develop completely inscrutable ways of reasoning, maybe even creating their own non-human languages, if doing so proves to be more effective.

Were the AI industry to proceed in that direction—seeking more powerful systems by giving up on legibility—"it would take away what was looking like it could have been an easy win" for AI safety, says Sam Bowman, the leader of a research department at Anthropic, an AI company, focused on "aligning" AI to human preferences. "We would be forfeiting an ability that we might otherwise have had to keep an eye on them.''',

    "document2": '''Two years ago, when big-name Chinese technology companies like Baidu and Alibaba were chasing Silicon Valley's advances in artificial intelligence with splashy announcements and new chatbots, DeepSeek took a different approach. It zeroed in on research.

The strategy paid off.

The Chinese start-up has jolted the tech world with its claim that it created a powerful A.I. model that was significantly cheaper to build than the offerings of its better-funded American rivals.

In the rivalry between China and the United States over domination of artificial intelligence, DeepSeek seemed to come out of nowhere. In fact, it has skyrocketed through China's tech world in recent years with a path that was anything but conventional.

Its mission to pursue research mirrors that of companies like OpenAI, the Silicon Valley firm that marked an American signature over A.I. in the fall of 2022. But the similarities mostly end there.''',

    "document3": '''When a small Chinese company called DeepSeek revealed that it had created an A.I. system that could match leading A.I. products made in the United States, the news was greeted in many circles as a warning that China was closing the gap in the global race to build artificial intelligence.

DeepSeek also said it built its new A.I. technology more cost effectively and with fewer hard-to-get computers chips than its American competitors, shocking an industry that had come to believe that bigger and better A.I. would cost billions and billions of dollars.'''
}

def load_documents():
    """Charger les documents depuis le dossier documents"""
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.txt'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_id = os.path.splitext(filename)[0]
                documents[doc_id] = f.read()

def search_documents(query):
    """Rechercher dans les documents"""
    results = []
    query = query.lower()
    
    for doc_id, content in documents.items():
        if query in content.lower():
            words = content.split()
            for i, word in enumerate(words):
                if query in word.lower():
                    start = max(0, i - 10)
                    end = min(len(words), i + 10)
                    excerpt = " ".join(words[start:end]) + "..."
                    results.append({
                        'doc_id': doc_id,
                        'excerpt': excerpt
                    })
                    break
    
    return results

@app.route('/')
def Index():
    return render_template("index.html")

@app.route('/formulaire', methods=["GET", "POST"])
def search():
    query = request.args.get('query', '') if request.method == 'GET' else request.form.get('query', '')
    if not query:
        return render_template("index.html", error="Veuillez entrer un terme de recherche")
    
    # Recharger les documents avant chaque recherche
    load_documents()
    results = search_documents(query)
    return render_template("index.html", results=results, query=query)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template("index.html", upload_error="Aucun fichier n'a été sélectionné")
    
    file = request.files['file']
    if file.filename == '':
        return render_template("index.html", upload_error="Aucun fichier n'a été sélectionné")
    
    if file and file.filename.endswith('.txt'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template("index.html", upload_success=f"Le fichier {filename} a été téléchargé avec succès")
    else:
        return render_template("index.html", upload_error="Seuls les fichiers .txt sont acceptés")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)