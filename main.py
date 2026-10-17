import tkinter as tk

root = tk.Tk()

root.title("Ganesh Nashta Center")

root.geometry("900x600")

title = tk.Label(
    root,
    text="Ganesh Nashta Center",
    font=("Arial", 24, "bold")
)

title.pack(pady=40)

subtitle = tk.Label(
    root,
    text="Sales & Business Intelligence Dashboard",
    font=("Arial", 16)
)

subtitle.pack(pady=10)

button = tk.Button(
    root,
    text="Start Application",
    font=("Arial", 14)
)

button.pack(pady=30)

root.mainloop()
