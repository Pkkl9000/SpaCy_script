from flask import Flask, request, jsonify
import spacy
from spacy import displacy

app = Flask(__name__)

# Загрузка английской модели
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    raise RuntimeError("English language model not found. Run: python -m spacy download en_core_web_lg")

@app.route('/full', methods=['POST'])
def full_analysis():
    """Полный анализ текста с максимальной информацией"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    try:
        doc = nlp(data['text'])
        result = []
        
        for token in doc:
            token_data = {
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "shape": token.shape_,
                "is_alpha": token.is_alpha,
                "is_stop": token.is_stop,
                "head": token.head.text,
                "head_pos": token.head.pos_,
                "children": [child.text for child in token.children],
                "ent_type": token.ent_type_ if token.ent_type_ else None,
                "ent_iob": token.ent_iob_,
                "morph": str(token.morph) if token.morph else None
            }
            result.append(token_data)

        # Добавляем именованные сущности
        entities = [{"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char} 
                   for ent in doc.ents]
        
        # Добавляем noun chunks
        noun_chunks = [{"text": chunk.text, "root": chunk.root.text} for chunk in doc.noun_chunks]

        return jsonify({
            "status": "success",
            "tokens": result,
            "entities": entities,
            "noun_chunks": noun_chunks,
            "sentence_count": len(list(doc.sents))
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/short', methods=['POST'])
def short_analysis():
    """Краткий анализ: часть речи, синтаксическая роль, head и children"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    try:
        doc = nlp(data['text'])
        result = []
        
        for token in doc:
            token_data = {
                "text": token.text,
                "pos": token.pos_,
                "dep": token.dep_,
                "head": token.head.text,
                "children": [child.text for child in token.children]
            }
            result.append(token_data)

        return jsonify({
            "status": "success",
            "tokens": result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tree', methods=['POST'])
def syntactic_tree():
    """Анализ текста с возвратом синтаксического дерева"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    try:
        doc = nlp(data['text'])
        
        # Создаем представление синтаксического дерева
        syntactic_tree = []
        for token in doc:
            syntactic_tree.append({
                "text": token.text,
                "dep": token.dep_,
                "dep_explained": spacy.explain(token.dep_),
                "head": token.head.text,
                "head_pos": token.head.pos_,
                "children": [{"text": child.text, "dep": child.dep_} for child in token.children]
            })

        return jsonify({
            "status": "success",
            "syntactic_tree": syntactic_tree,
            "sentence_count": len(list(doc.sents))
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain_terms():
    """Объяснение терминов SpaCy"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if 'terms' not in data:
        return jsonify({"error": "Missing 'terms' field"}), 400

    terms = data['terms']
    explanations = {term: spacy.explain(term) or "Explanation not found" for term in terms}

    return jsonify({"explanations": explanations}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервиса"""
    return jsonify({"status": "healthy", "model": "en_core_web_lg"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
