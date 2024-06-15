# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import random

class TesterApp:
    def __init__(self, root, width=800, height=600):
        self.root = root
        self.root.title("SmartTest")
        self.window_width = width
        self.window_height = height
        
        self.load_questions()
        self.results_file = "results.json"
        self.load_results()
        
        self.user_name = tk.StringVar()
        self.user_surname = tk.StringVar()
        self.user_patronymic = tk.StringVar()
        self.selected_topic = tk.StringVar()
        self.randomize_questions = tk.BooleanVar()

        self.current_question_index = 0
        self.correct_answers_count = 0
        self.user_answers = []

        self.user_name.trace("w", lambda *args: self.update_results_display())
        self.user_surname.trace("w", lambda *args: self.update_results_display())
        self.user_patronymic.trace("w", lambda *args: self.update_results_display())

        self.setup_start_screen()

    def load_questions(self):
        with open('questions.json', 'r', encoding='utf-8-sig') as file:
            self.questions = json.load(file)
        self.topics = sorted(set(q["topic"] for q in self.questions))

    def load_results(self):
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r', encoding='utf-8') as file:
                try:
                    self.results = json.load(file)
                except json.JSONDecodeError:
                    self.results = {}
        else:
            self.results = {}

    def save_results(self):
        with open(self.results_file, 'w', encoding='utf-8') as file:
            json.dump(self.results, file, ensure_ascii=False, indent=4)

    def get_user_key(self):
        return f"{self.user_surname.get()}_{self.user_name.get()}_{self.user_patronymic.get()}"

    def setup_start_screen(self):
        self.clear_window()
        self.center_window()

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        input_frame = tk.Frame(main_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        center_frame = tk.Frame(input_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        results_frame = tk.Frame(main_frame, bg="lightgrey", bd=1, relief=tk.SOLID)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(center_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(center_frame, textvariable=self.user_name).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(center_frame, text="Фамилия:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(center_frame, textvariable=self.user_surname).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(center_frame, text="Отчество:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(center_frame, textvariable=self.user_patronymic).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(center_frame, text="Выберите тематику:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Combobox(center_frame, textvariable=self.selected_topic, values=self.topics).grid(row=3, column=1, padx=5, pady=5)
        
        tk.Checkbutton(center_frame, text="Включить случайность вопросов", variable=self.randomize_questions).grid(row=4, columnspan=2, padx=5, pady=5)
        
        tk.Button(center_frame, text="Дальше", command=self.start_test).grid(row=5, columnspan=2, padx=5, pady=5)

        self.results_label = tk.Label(results_frame, text="", bg="lightgrey", justify=tk.LEFT, anchor="nw")
        self.results_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_results_display()

    def update_results_display(self):
        user_key = self.get_user_key()
        if not self.user_name.get() or not self.user_surname.get() or not self.user_patronymic.get():
            self.results_label.config(text="Введите имя, фамилию и отчество.")
            return

        if user_key in self.results:
            results_text = f"Результаты тестов {len(self.results[user_key])}/{len(self.topics)}\n\n"
            for topic in self.topics:
                if topic in self.results[user_key]:
                    result = self.results[user_key][topic]
                    results_text += f"{self.user_name.get()} {self.user_surname.get()} {self.user_patronymic.get()} {result['correct']}/{result['total']} тест {topic}\n"
                else:
                    results_text += f"{self.user_name.get()} {self.user_surname.get()} {self.user_patronymic.get()} еще не проходил тест {topic}\n"
            self.results_label.config(text=results_text)
        else:
            self.results_label.config(text=f"Результаты тестов 0/{len(self.topics)}\n\n{self.user_name.get()} {self.user_surname.get()} {self.user_patronymic.get()} еще не проходил ни одного теста.")

    def start_test(self):
        if not self.user_name.get() or not self.user_surname.get() or not self.user_patronymic.get():
            messagebox.showwarning("Ошибка", "Пожалуйста, введите имя, фамилию и отчество.")
            return

        if not self.selected_topic.get():
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите тематику.")
            return

        self.filtered_questions = [q for q in self.questions if q["topic"] == self.selected_topic.get()]

        if self.randomize_questions.get():
            random.shuffle(self.filtered_questions)
            for question in self.filtered_questions:
                random.shuffle(question["answers"])

        self.current_question_index = 0
        self.correct_answers_count = 0
        self.user_answers = []
        
        self.setup_test_screen()

    def setup_test_screen(self):
        self.clear_window()
        self.center_window()
        
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate", maximum=len(self.filtered_questions))
        self.progress.pack(pady=10)
        self.update_progress_bar()

        question_frame = tk.Frame(frame, bg="white", bd=2, relief=tk.SOLID)
        question_frame.pack(fill=tk.X, padx=10, pady=10)

        question = self.filtered_questions[self.current_question_index]
        tk.Label(question_frame, text=question["question"], bg="white", wraplength=760, justify=tk.LEFT).pack(pady=10, padx=10)

        answers_frame = tk.Frame(frame)
        answers_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.answer_vars = []

        if question["multiple"]:
            for i, answer in enumerate(question["answers"]):
                var = tk.BooleanVar()
                tk.Checkbutton(answers_frame, text=answer, variable=var, command=self.check_answer_selected).pack(anchor="w", pady=5, padx=10)
                self.answer_vars.append(var)
        else:
            self.answer_var = tk.StringVar()
            self.answer_var.set(None)
            for i, answer in enumerate(question["answers"]):
                tk.Radiobutton(answers_frame, text=answer, variable=self.answer_var, value=answer, command=self.check_answer_selected).pack(anchor="w", pady=5, padx=10)

        self.next_button = tk.Button(frame, text="Дальше", command=self.next_question)
        self.next_button.pack(pady=10)
        self.next_button.pack_forget()

    def update_progress_bar(self):
        self.progress['value'] = self.current_question_index

    def check_answer_selected(self):
        question = self.filtered_questions[self.current_question_index]
        if question["multiple"]:
            if any(var.get() for var in self.answer_vars):
                self.next_button.pack()
            else:
                self.next_button.pack_forget()
        else:
            if self.answer_var.get():
                self.next_button.pack()
            else:
                self.next_button.pack_forget()

    def next_question(self):
        question = self.filtered_questions[self.current_question_index]
        if question["multiple"]:
            user_answer = [var.get() for var in self.answer_vars]
        else:
            user_answer = self.answer_var.get()
        
        self.user_answers.append(user_answer)
        
        if question["multiple"]:
            correct_answers_set = set(question["correct_answers"])
            user_answers_set = set([question["answers"][i] for i, var in enumerate(self.answer_vars) if var.get()])
            if correct_answers_set == user_answers_set:
                self.correct_answers_count += 1
        else:
            if user_answer in question["correct_answers"]:
                self.correct_answers_count += 1

        self.current_question_index += 1

        if self.current_question_index < len(self.filtered_questions):
            self.setup_test_screen()
        else:
            self.save_current_results()
            self.show_results()

    def save_current_results(self):
        user_key = self.get_user_key()
        topic = self.selected_topic.get()
        if user_key not in self.results:
            self.results[user_key] = {}
        self.results[user_key][topic] = {
            "correct": self.correct_answers_count,
            "total": len(self.filtered_questions)
        }
        self.save_results()

    def show_results(self):
        self.clear_window()
        self.center_window()
        
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        tk.Label(frame, text=f"Результаты для {self.user_name.get()} {self.user_surname.get()} {self.user_patronymic.get()}").grid(row=0, column=0, columnspan=2, pady=5)
        tk.Label(frame, text=f"Правильных ответов: {self.correct_answers_count}/{len(self.filtered_questions)}").grid(row=1, column=0, columnspan=2, pady=5)

        tk.Button(frame, text="Пройти снова", command=self.setup_start_screen).grid(row=2, column=0, columnspan=2, pady=5)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def center_window(self):
        self.root.update_idletasks()
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        width = self.window_width
        height = self.window_height
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

if __name__ == "__main__":
    root = tk.Tk()
    app = TesterApp(root, width=800, height=600)
    root.mainloop()
