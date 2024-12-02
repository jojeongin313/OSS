import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
import json
import os

# 후보 리스트를 담을 변수
candidates = []
round_number = 1
total_candidates = 0
title = ""

# 이미지 업로드 함수
def upload_image():
    file_path = filedialog.askopenfilename(title="이미지 파일 선택", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        image = Image.open(file_path)
        image.thumbnail((200, 200))  # 이미지 크기 조정
        return ImageTk.PhotoImage(image), file_path
    return None, None

# 후보 추가 함수
def add_candidate():
    name = name_entry.get()
    image, image_path = upload_image()
    if name and image:
        candidates.append({'name': name, 'image': image, 'image_path': image_path})
        listbox.insert(tk.END, name)  # 후보 리스트 박스에 이름 추가
        name_entry.delete(0, tk.END)  # 이름 입력란 초기화

# 대진표 크기 설정 (8강, 16강, 32강, 64강)
def set_tournament_size():
    global total_candidates
    size = tournament_size_var.get()
    if size == 8:
        total_candidates = 8
    elif size == 16:
        total_candidates = 16
    elif size == 32:
        total_candidates = 32
    elif size == 64:
        total_candidates = 64
    candidates.clear()  # 후보 초기화
    listbox.delete(0, tk.END)  # 리스트 박스 초기화
    result_label.config(text="후보를 추가하세요.")

# 대진표 시작
def start_tournament():
    global round_number
    round_number = 1
    if len(candidates) < total_candidates:
        result_label.config(text=f"{total_candidates}명의 후보가 필요합니다!")
        return
    
    # 후보 수가 많으면 무작위로 8명만 추출
    if len(candidates) > total_candidates:
        candidates_selected = random.sample(candidates, total_candidates)
    else:
        candidates_selected = candidates

    random.shuffle(candidates_selected)  # 후보들을 무작위로 섞기
    next_round_candidates = [candidates_selected[i] for i in range(len(candidates_selected))]
    run_round(next_round_candidates)

# 라운드 진행 함수
def run_round(candidates_in_round):
    global round_number
    if len(candidates_in_round) == 1:
        result_label.config(text=f"최종 승자: {candidates_in_round[0]['name']}")
        return
    if len(candidates_in_round) % 2 != 0:
        candidates_in_round.append(candidates_in_round[-1])  # 홀수일 때 자동 승자 처리

    # 1:1 대결
    round_display.config(text=f"{round_number}라운드")
    candidate1 = candidates_in_round[0]
    candidate2 = candidates_in_round[1]
    
    # 이미지 및 이름 표시
    candidate1_label.config(image=candidate1['image'], text=candidate1['name'], compound="top")
    candidate2_label.config(image=candidate2['image'], text=candidate2['name'], compound="top")
    
    # 버튼 클릭 시 승자 선택
    def select_winner(winner):
        nonlocal candidates_in_round
        if winner == 1:
            next_round_candidates = candidates_in_round[::2]  # 1번 승자
        else:
            next_round_candidates = candidates_in_round[1::2]  # 2번 승자
        round_number += 1
        run_round(next_round_candidates)

    button1 = tk.Button(window, text=f"{candidate1['name']} 승자", command=lambda: select_winner(1))
    button2 = tk.Button(window, text=f"{candidate2['name']} 승자", command=lambda: select_winner(2))
    
    button1.pack()
    button2.pack()

# 타이틀 입력 및 저장
def save_tournament():
    global title
    title = title_entry.get()
    if not title:
        result_label.config(text="타이틀을 입력해주세요.")
        return
    
    tournament_data = {
        'title': title,
        'size': total_candidates,
        'candidates': [{'name': c['name'], 'image_path': c['image_path']} for c in candidates]
    }

    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(tournament_data, file)
        result_label.config(text="이상형 월드컵이 저장되었습니다.")

# 저장된 대회 불러오기
def load_tournament():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as file:
            tournament_data = json.load(file)
        title_entry.delete(0, tk.END)
        title_entry.insert(0, tournament_data['title'])
        set_tournament_size_from_file(tournament_data['size'])
        candidates.clear()
        listbox.delete(0, tk.END)
        for c in tournament_data['candidates']:
            name = c['name']
            image, _ = upload_image_for_existing(c['image_path'])
            candidates.append({'name': name, 'image': image, 'image_path': c['image_path']})
            listbox.insert(tk.END, name)
        result_label.config(text=f"{tournament_data['title']} 대회를 불러왔습니다.")

# 대진표 크기 설정 (파일로부터 로드)
def set_tournament_size_from_file(size):
    global total_candidates
    total_candidates = size
    if size == 8:
        tournament_size_var.set(8)
    elif size == 16:
        tournament_size_var.set(16)
    elif size == 32:
        tournament_size_var.set(32)
    elif size == 64:
        tournament_size_var.set(64)

# 이미지 업로드 (기존 파일에서)
def upload_image_for_existing(image_path):
    image = Image.open(image_path)
    image.thumbnail((200, 200))
    return ImageTk.PhotoImage(image)

# GUI 설정
window = tk.Tk()
window.title("이상형 월드컵 소프트웨어")
window.geometry("1000x800")

# 타이틀 입력란
title_label = tk.Label(window, text="대회 타이틀 입력", font=("Arial", 14))
title_label.pack(pady=10)
title_entry = tk.Entry(window, font=("Arial", 12))
title_entry.pack(pady=5)

# 라운드 크기 설정
tournament_size_label = tk.Label(window, text="대진표 크기 선택", font=("Arial", 14))
tournament_size_label.pack(pady=10)

# 라운드 크기 선택 (8강, 16강, 32강, 64강)
tournament_size_var = tk.IntVar()
tournament_size_var.set(8)
tournament_size_8 = tk.Radiobutton(window, text="8강", variable=tournament_size_var, value=8, font=("Arial", 12))
tournament_size_8.pack()
tournament_size_16 = tk.Radiobutton(window, text="16강", variable=tournament_size_var, value=16, font=("Arial", 12))
tournament_size_16.pack()
tournament_size_32 = tk.Radiobutton(window, text="32강", variable=tournament_size_var, value=32, font=("Arial", 12))
tournament_size_32.pack()
tournament_size_64 = tk.Radiobutton(window, text="64강", variable=tournament_size_var, value=64, font=("Arial", 12))
tournament_size_64.pack()

# 라운드 크기 설정 버튼
set_size_button = tk.Button(window, text="대진표 크기 설정", command=set_tournament_size, font=("Arial", 12))
set_size_button.pack(pady=10)

# 후보 추가 UI
name_label = tk.Label(window, text="후보 이름 입력", font=("Arial", 14))
name_label.pack(pady=10)
name_entry = tk.Entry(window, font=("Arial", 12))
name_entry.pack(pady=5)

add_button = tk.Button(window, text="후보 추가", command=add_candidate, font=("Arial", 12))
add_button.pack(pady=10)

# 후보 리스트
listbox = tk.Listbox(window, font=("Arial", 12), height=10, width=50)
listbox.pack(pady=10)

# 대진표 시작
start_button = tk.Button(window, text="대진표 시작", command=start_tournament, font=("Arial", 14))
start_button.pack(pady=20)

# 대회 저장 및 불러오기
save_button = tk.Button(window, text="대회 저장", command=save_tournament, font=("Arial", 14))
save_button.pack(pady=10)

load_button = tk.Button(window, text="대회 불러오기", command=load_tournament, font=("Arial", 14))
load_button.pack(pady=10)

# 결과 표시 레이블
result_label = tk.Label(window, text="", font=("Arial", 16))
result_label.pack(pady=20)

# 이미지 및 이름 표시
candidate1_label = tk.Label(window, text="", font=("Arial", 12))
candidate1_label.pack(pady=10)

candidate2_label = tk.Label(window, text="", font=("Arial", 12))
candidate2_label.pack(pady=10)

# 결과 표시
round_display = tk.Label(window, text="", font=("Arial", 14))
round_display.pack(pady=20)

# 실행
window.mainloop()
