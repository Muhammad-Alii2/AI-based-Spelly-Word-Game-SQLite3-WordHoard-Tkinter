import random
import sqlite3
from wordhoard import Definitions
import tkinter as tk
from tkinter import messagebox, Button, Label, Radiobutton, END, LEFT, DISABLED, NORMAL, VERTICAL, RIGHT, Y


def addWord(word):
    try:
        connection = sqlite3.connect('mydb')
        cursor = connection.cursor()
        cursor.execute('insert into Wordlist (word) values (?)', (word,))
        connection.commit()
        message = 'Added ' + word + ' into the Wordlist'
    except sqlite3.Error as e:
        message = 'Error occurred:' + str(e)
    finally:
        connection.close()
    return message


def readWords():
    try:
        connection = sqlite3.connect('mydb')
        cursor = connection.cursor()
        cursor.execute('select * from Wordlist')
        message = cursor.fetchall()
    except sqlite3.Error as e:
        message = 'Error occurred:' + str(e)
    finally:
        connection.close()
    return message


def updateWord(old_word, new_word):
    try:
        connection = sqlite3.connect('mydb')
        cursor = connection.cursor()
        cursor.execute('update Wordlist set Word = ? where Word = ?', (new_word, old_word))
        connection.commit()
        message = 'Updated ' + old_word + ' with ' + new_word
    except sqlite3.Error as e:
        message = 'Error occurred:' + str(e)
    finally:
        connection.close()
    return message


def deleteWord(word):
    try:
        connection = sqlite3.connect('mydb')
        cursor = connection.cursor()
        cursor.execute('delete from Wordlist where Word = ?', (word,))
        connection.commit()
        message = 'Deleted ' + word + ' from the Wordlist'
    except sqlite3.Error as e:
        message = 'Error occurred:' + str(e)
    finally:
        connection.close()
    return message


def validateWord(word, wordlist):
    return word.lower() in wordlist


def aiOpponentEasy(player_word, word_list, used_words):
    last_letter = player_word[-1]
    possible_words = [word for word in word_list if word.startswith(last_letter) and word not in used_words]
    if possible_words:
        opponent_word = min(possible_words, key=len)
        return opponent_word
    else:
        return None


def aiOpponentMedium(player_word, word_list, used_words):
    last_letter = player_word[-1]
    possible_words = [word for word in word_list if word.startswith(last_letter) and word not in used_words]
    if possible_words:
        opponent_word = random.choice(possible_words)
        return opponent_word
    else:
        return None


def aiOpponentHard(player_word, word_list, used_words):
    last_letter = player_word[-1]
    possible_words = [word for word in word_list if word.startswith(last_letter) and word not in used_words]
    if possible_words:
        opponent_word = max(possible_words, key=len)
        return opponent_word
    else:
        return None


def shuffleWord(word):
    shuffled_word = list(word)
    random.shuffle(shuffled_word)
    return ''.join(shuffled_word)


def startGame():
    root.withdraw()
    game_window = tk.Toplevel(root)
    game_window.title("Word Game")

    current_word = tk.StringVar()
    shuffled_word = tk.StringVar()
    player_score = tk.IntVar()
    opponent_score = tk.IntVar()
    turn = tk.StringVar()
    used_words = []
    entry_state = "guess"

    def initGame():
        nonlocal current_word, shuffled_word, used_words
        player_score.set(0)
        opponent_score.set(0)
        current_word.set(random.choice(word_list))
        shuffled_word.set(shuffleWord(current_word.get()))
        turn.set("Player's Turn")
        updateLabels()

    def updateLabels():
        current_word_label.config(text="Shuffled word: " + shuffled_word.get())
        player_score_label.config(text="Player score: " + str(player_score.get()))
        opponent_score_label.config(text="Opponent score: " + str(opponent_score.get()))
        # used_words_label.config(text="Used words: " + ', '.join(used_words))
        turn_label.config(text=turn.get())

    def processTurn():
        nonlocal current_word, entry_state
        player_word = player_word_entry.get().strip().lower()
        if entry_state == 'guess':
            if player_word == current_word.get():
                player_word_entry.delete(0, END)
                entry_state = 'entry'
                messagebox.showinfo('Correct Guess','Your guess is correct. You can enter your word now')
            else:
                messagebox.showerror("Incorrect Guess", "Your guess is incorrect. Try again!")
        elif entry_state=='entry':
            if not player_word:
                messagebox.showerror("Error", "Please enter a word.")
                return

            if player_word[0] != current_word.get()[-1]:
                messagebox.showerror("Error", "Your word must start with the last letter of the current word, i.e " +
                                     current_word.get()[-1])
                return

            if player_word not in word_list:
                messagebox.showerror("Error", "Invalid word. Please try again.")
                return

            if player_word in used_words:
                messagebox.showerror("Error", "This word has already been used. Please use another word.")
                return

            player_word_entry.delete(0, END)
            entry_state = 'guess'
            used_words.append(player_word)
            player_score.set(player_score.get() + len(player_word))
            checkWinner()
            current_word.set(player_word)
            turn.set("Opponent's Turn")
            updateLabels()
            disableButtons()
            root.after(5000, opponentTurn)

    def opponentTurn():
        nonlocal current_word
        if difficulty.get() == 2:
            opponent_word = aiOpponentHard(current_word.get(), word_list, used_words)
        elif difficulty.get() == 1:
            opponent_word = aiOpponentMedium(current_word.get(), word_list, used_words)
        else:
            opponent_word = aiOpponentEasy(current_word.get(), word_list, used_words)

        if opponent_word:
            used_words.append(opponent_word)
            opponent_score.set(opponent_score.get() + len(opponent_word))
            checkWinner()
            current_word.set(opponent_word)
            shuffled_word.set(shuffleWord(current_word.get()))
            turn.set("Player's Turn")
        else:
            messagebox.showinfo('Congratulations!', 'Opponent could not find a valid word. You win!')
            game_window.destroy()

        enableButtons()
        updateLabels()

    def wordHint():
        definition = Definitions(search_string=current_word.get())
        definition_results = definition.find_definitions()
        print(definition_results)
        if definition_results:
            messagebox.showinfo("Hint", definition_results[0])
        else:
            messagebox.showerror('Error!', 'No hint available')

    def enableButtons():
        submit_button.config(state=NORMAL)
        hint_button.config(state=NORMAL)

    def disableButtons():
        submit_button.config(state=DISABLED)
        hint_button.config(state=DISABLED)

    def checkWinner():
        nonlocal player_score, opponent_score
        if player_score.get() >= 100:
            messagebox.showinfo("Game Over", "You win!")
            game_window.destroy()
        elif opponent_score.get() >= 100:
            messagebox.showinfo("Game Over", "Opponent wins!")
            game_window.destroy()

    def onClosing():
        game_window.destroy()
        root.deiconify()

    game_window.protocol("WM_DELETE_WINDOW", onClosing)

    frame = tk.Frame(game_window)
    frame.pack(padx=10, pady=10)
    turn_label = Label(frame, text="")
    turn_label.pack()
    current_word_label = tk.Label(frame, text='Current Word: ')
    current_word_label.pack()
    player_word_entry = tk.Entry(frame)
    player_word_entry.pack()
    submit_button = tk.Button(frame, text="Submit", command=processTurn)
    submit_button.pack()
    hint_button = Button(frame, text="Hint", command=wordHint)
    hint_button.pack()
    player_score_label = Label(frame, text="")
    player_score_label.pack()
    opponent_score_label = Label(frame, text="")
    opponent_score_label.pack()
    # used_words_label = Label(frame, text="")
    # used_words_label.pack()

    initGame()


def addDialog():
    add_window = tk.Toplevel(root)
    add_window.title("Add Word")

    def add_word():
        word = word_entry.get().strip()
        if word:
            message = addWord(word)
            messagebox.showinfo("Return Message", message)
            word_entry.delete(0, END)
        else:
            messagebox.showerror("Error", "Please enter a word.")

    word_label = Label(add_window, text="Enter word to add:")
    word_label.pack()
    word_entry = tk.Entry(add_window)
    word_entry.pack()
    add_button = Button(add_window, text="Add", command=add_word)
    add_button.pack()


def readDialog():
    read_window = tk.Toplevel(root)
    read_window.title("Word List")

    words = readWords()
    word_list = [word[1] for word in words]
    word_text = tk.Text(read_window)
    word_text.pack(side=LEFT)
    word_text.insert(END, "\n".join(word_list))
    scrollbar = tk.Scrollbar(read_window, orient=VERTICAL, command=word_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    word_text.config(yscrollcommand=scrollbar.set)


def updateDialog():
    update_window = tk.Toplevel(root)
    update_window.title("Update Word")

    def update_word_in_list():
        old_word = old_word_entry.get().strip()
        new_word = new_word_entry.get().strip()
        if old_word and new_word:
            message =  updateWord(old_word, new_word)
            messagebox.showinfo("Return Message", message)
            old_word_entry.delete(0, END)
            new_word_entry.delete(0, END)
        else:
            messagebox.showerror("Error", "Please enter both old and new words.")

    old_word_label = Label(update_window, text="Old word:")
    old_word_label.pack()
    old_word_entry = tk.Entry(update_window)
    old_word_entry.pack()
    new_word_label = Label(update_window, text="New word:")
    new_word_label.pack()
    new_word_entry = tk.Entry(update_window)
    new_word_entry.pack()
    update_button = Button(update_window, text="Update", command=update_word_in_list)
    update_button.pack()


def deleteDialog():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Word")

    def delete_word_from_list():
        word = word_entry.get().strip()
        if word:
            message = deleteWord(word)
            messagebox.showinfo("Return Message", message)
            word_entry.delete(0, END)
        else:
            messagebox.showerror("Error", "Please enter a word.")

    word_label = Label(delete_window, text="Enter word to delete:")
    word_label.pack()
    word_entry = tk.Entry(delete_window)
    word_entry.pack()
    delete_button = Button(delete_window, text="Delete", command=delete_word_from_list)
    delete_button.pack()


# Main GUI Code
root = tk.Tk()
root.title('SPELLY Word Game')

word_tuple = readWords()
word_list = [word[1] for word in word_tuple]

difficulty = tk.IntVar(value=1)

spelly_label = tk.Label(root, text='SPELLY', font=('Arial', 20, 'bold'))
spelly_label.pack()

difficulty_frame = tk.Frame(root)
difficulty_frame.pack()
Label(difficulty_frame, text="Difficulty: ").pack()
Radiobutton(difficulty_frame, text="Easy", variable=difficulty, value=0).pack(side=LEFT)
Radiobutton(difficulty_frame, text="Medium", variable=difficulty, value=1).pack(side=LEFT)
Radiobutton(difficulty_frame, text="Hard", variable=difficulty, value=2).pack(side=LEFT)
start_game_button = Button(root, text="Start Game", command=startGame)
start_game_button.pack(padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack()
word_mgt_label = tk.Label(button_frame, text='Words Management:', font=('Arial', 13))
word_mgt_label.pack()
add_button = tk.Button(button_frame, text="Add", command=addDialog)
add_button.pack(side=tk.LEFT, padx=5, pady=5)
read_button = tk.Button(button_frame, text="Read", command=readDialog)
read_button.pack(side=tk.LEFT, padx=5, pady=5)
update_button = tk.Button(button_frame, text="Update", command=updateDialog)
update_button.pack(side=tk.LEFT, padx=5, pady=5)
delete_button = tk.Button(button_frame, text="Delete", command=deleteDialog)
delete_button.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()
