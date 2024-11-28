
import tkinter as tk

from tkinter import messagebox,ttk

import re
	
import nltk

from langdetect import detect

import pickle


try:

    nltk.download('punkt_tab')

except Exception as e:

    messagebox.showerror("Error", f"Failed to download NLTK data: {e}")



def save_model(trie, filename):

    with open(filename, 'wb') as file:

        pickle.dump(trie, file)

    print(f"Model saved to {filename}")



def load_model(filename):

    with open(filename, 'rb') as file:

        trie = pickle.load(file)

    print(f"Model loaded from {filename}")

    return trie



def load_dataset(file_path):

    try:

        with open(file_path, 'r', encoding='latin-1') as file:

            data = file.read().lower()

        data = re.sub(r'\s+', ' ', data)

        print(f"Dataset loaded from {file_path}")  

        return data

    except FileNotFoundError:

        messagebox.showerror("Error", "File not found.")

        return ""

    except Exception as e:

        messagebox.showerror("Error", f"Failed to load dataset: {e}")

        return ""


class TrieNode:

    def __init__(self):

        self.children = {}

        self.count = 0


class Trie:

    def __init__(self):

        self.root = TrieNode()


    def insert(self, words):

        node = self.root

        for word in words:

            if word not in node.children:

                node.children[word] = TrieNode()

            node = node.children[word]

        node.count += 1


    def get_suggestions(self, prefix):

        node = self.root

        for word in prefix:

            if word in node.children:

                node = node.children[word]

            else:

                return []

        return self._collect_suggestions(node, prefix)


    def _collect_suggestions(self, node, prefix):

        suggestions = []

        if node.count > 0:

            suggestions.append((' '.join(prefix), node.count))

        for word, child in node.children.items():

            suggestions.extend(self._collect_suggestions(child, prefix + [word]))

        return suggestions


def build_phrase_trie_model(text):

    sentences = nltk.sent_tokenize(text)

    trie = Trie()

    for sentence in sentences:

        words = nltk.word_tokenize(sentence)

        trie.insert(words)

    print(f"Trie model built with {len(sentences)} sentences.")  

    return trie


def get_full_sentence_suggestion(trie, prefix):

    tokens = nltk.word_tokenize(prefix)

    print(f"Searching for suggestion with prefix: {tokens}")  

    suggestions = trie.get_suggestions(tokens)

    if suggestions:

        print(f"Suggestion found: {suggestions[0][0]}")  

        return suggestions[0][0]  

    print("No suggestion found."," ", tokens[-1])

    if tokens[-1]=='.':

        trie.insert(tokens)

        print("inserted")  

    return ""




def detect_language(text):

    try:

        detected_lang = detect(text)

        print(f"Language detected: {detected_lang}")  

        return detected_lang

    except Exception:

        print("Failed to detect language.")  

        return None


class AutocompleteBox(tk.Tk):

    def __init__(self, eng_trie):

        super().__init__()

        self.title("Autocomplete Text Box")

        self.geometry("800x600")


        self.eng_trie = eng_trie  

        self.it_trie = it_trie_model  

        self.current_trie = eng_trie  


        self.language_var = tk.StringVar(value="English")

        self.language_dropdown = ttk.Combobox(self, textvariable=self.language_var, values=["English", "Italian"])

        self.language_dropdown.pack(pady=10)

        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)


        self.text_widget = tk.Text(self, wrap=tk.WORD, font=("Helvetica", 16), undo=True)

        self.text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.text_widget.bind("<KeyRelease>", self.on_key_release)

        self.text_widget.bind("<Return>", self.on_enter)

        self.text_widget.bind("<Down>", self.on_down_arrow)


        self.text_widget.tag_configure("suggestion", foreground="lightgray")


        self.suggestions = []  

        self.suggestion_index = -1  


    def change_language(self, event=None):

        selected_language = self.language_var.get()

        if selected_language == "Italian":

            self.current_trie = self.it_trie

        else:

            self.current_trie = self.eng_trie

        print(f"Language switched to {selected_language}")


    def on_key_release(self, event):

        if event.keysym in ["Up", "Down", "Left", "Right", "Return", "Shift_L", "Shift_R", "Caps_Lock"]:

            return


        if self.text_widget.tag_ranges("suggestion"):

            self.clear_suggestion()


        user_input = self.text_widget.get("1.0", tk.END).strip()


        last_sentence = self.get_last_sentence(user_input)

        dd=nltk.word_tokenize(last_sentence)

        print(dd)

        if last_sentence:

            self.suggestions = self.get_all_suggestions(last_sentence)

            self.suggestion_index = 0  

            if self.suggestions:


                self.show_inline_suggestion(last_sentence, self.suggestions[self.suggestion_index])


        elif dd[-1]=='.':

            self.trie.insert(dd)

        else:

            self.clear_suggestion()


    def get_last_sentence(self, text):

        sentences = re.split(r'(?<=[.!?])\s+', text)

        return sentences[-1].strip()


    def get_all_suggestions(self, text):

        tokens = nltk.word_tokenize(text)

        suggestions = self.current_trie.get_suggestions(tokens)


        return [suggestion[0] for suggestion in sorted(suggestions, key=lambda x: x[1], reverse=True)]


    def show_inline_suggestion(self, current_text, suggestion):

        if suggestion.startswith(current_text) and not self.text_widget.tag_ranges("suggestion"):

            predicted_text = suggestion[len(current_text):].strip()

            if predicted_text:

                self.clear_suggestion()

                self.text_widget.insert(tk.END, predicted_text, "suggestion")

            else:

                self.clear_suggestion()

        else:

            self.clear_suggestion()


    def clear_suggestion(self):

        suggestion_ranges = self.text_widget.tag_ranges("suggestion")

        if suggestion_ranges:

            self.text_widget.delete(suggestion_ranges[0], suggestion_ranges[1])

        self.text_widget.tag_remove("suggestion", "1.0", tk.END)


    def on_enter(self, event):

        suggestion_ranges = self.text_widget.tag_ranges("suggestion")

        if suggestion_ranges:

            suggestion_text = self.text_widget.get(suggestion_ranges[0], suggestion_ranges[1])

            self.text_widget.insert(tk.END, suggestion_text)

            self.clear_suggestion()


        return "break"

    def on_down_arrow(self, event):


        if self.suggestions:

            self.suggestion_index = (self.suggestion_index + 1) % len(self.suggestions)

            current_text = self.get_last_sentence(self.text_widget.get("1.0", tk.END).strip())

            self.show_inline_suggestion(current_text, self.suggestions[self.suggestion_index])




eng_dataset = load_dataset("cjtext.txt")

eng_trie_model = build_phrase_trie_model(eng_dataset)

save_model(eng_trie_model, "eng_trie_model.pkl") 


it_dataset = load_dataset("cjtextItalian.txt")

it_trie_model = build_phrase_trie_model(it_dataset)

save_model(it_trie_model, "it_trie_model.pkl")  



eng_trie_model = load_model("eng_trie_model.pkl")

it_trie_model = load_model("it_trie_model.pkl")


if __name__ == "__main__":

    app = AutocompleteBox(eng_trie_model) 

    app.mainloop()




