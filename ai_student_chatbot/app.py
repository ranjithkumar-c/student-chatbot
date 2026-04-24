from flask import Flask, render_template, request, jsonify
import json
import random
import os
import difflib

app = Flask(__name__)

# -------------------------------
# FILE SETUP
# -------------------------------
FILE_NAME = "knowledge.json"

default_knowledge = {
    "hello": ["Hi! How can I help you?", "Hello! Ask me your doubt."],
    "hi": ["Hey there! What do you need help with?"],
    "what is python": ["Python is a programming language used in AI, web, and more."],
    "what is ai": ["AI stands for Artificial Intelligence."],
    "what is dbms": ["DBMS stands for Database Management System."],
    "what is os": ["OS means Operating System."],
    "what is cpu": ["CPU is the brain of the computer."],
    "what is ram": ["RAM is temporary memory used during execution."],
    "algorithm": ["An algorithm is a step-by-step solution to a problem."],
    "data structure": ["A data structure is used to organize data."]
}

# Create file if not exists
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as f:
        json.dump(default_knowledge, f, indent=4)

# Load knowledge
with open(FILE_NAME, "r") as f:
    knowledge = json.load(f)

# -------------------------------
# MEMORY (STATE)
# -------------------------------
memory = {
    "name": None,
    "last_topic": None,
    "learning": False,
    "pending_question": None
}

# -------------------------------
# SAVE KNOWLEDGE
# -------------------------------
def save_knowledge():
    with open(FILE_NAME, "w") as f:
        json.dump(knowledge, f, indent=4)

# -------------------------------
# SMART MATCH
# -------------------------------
def get_best_match(user_input):
    keys = list(knowledge.keys())
    match = difflib.get_close_matches(user_input, keys, n=1, cutoff=0.5)
    return match[0] if match else None

# -------------------------------
# CHATBOT FUNCTION
# -------------------------------
def chatbot(user_input):
    user_input = user_input.lower().strip()

    # -------------------------------
    # LEARNING FLOW (STEP 2: USER GIVES ANSWER)
    # -------------------------------
    if memory["learning"]:
        answer = user_input
        question = memory["pending_question"]

        if question in knowledge:
            knowledge[question].append(answer)
        else:
            knowledge[question] = [answer]

        save_knowledge()

        memory["learning"] = False
        memory["pending_question"] = None

        return "✅ Got it! I learned something new."

    # -------------------------------
    # STEP 1: USER SAYS YES/NO
    # -------------------------------
    if user_input == "yes" and memory["pending_question"]:
        memory["learning"] = True
        return "Please enter the correct answer."

    if user_input == "no" and memory["pending_question"]:
        memory["pending_question"] = None
        return "Okay, no problem!"

    # -------------------------------
    # MEMORY FEATURES
    # -------------------------------
    if "my name is" in user_input:
        name = user_input.split("my name is")[-1].strip()
        memory["name"] = name
        return f"Nice to meet you, {name}! 😊"

    if "what is my name" in user_input:
        return memory["name"] or "I don't know your name yet."

    # -------------------------------
    # FOLLOW-UP
    # -------------------------------
    if user_input in ["more", "explain more"]:
        if memory["last_topic"]:
            return random.choice(knowledge[memory["last_topic"]])
        return "Ask something first."

    # -------------------------------
    # DIRECT MATCH
    # -------------------------------
    for key in knowledge:
        if key in user_input:
            memory["last_topic"] = key
            return random.choice(knowledge[key])

    # -------------------------------
    # SMART MATCH
    # -------------------------------
    best_match = get_best_match(user_input)
    if best_match:
        memory["last_topic"] = best_match
        return random.choice(knowledge[best_match])

    # -------------------------------
    # ASK TO TEACH
    # -------------------------------
    memory["pending_question"] = user_input
    return "I don't know that yet 🤔\nWould you like to teach me? (yes/no)"

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    response = chatbot(user_input)
    return jsonify({"reply": response})

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)