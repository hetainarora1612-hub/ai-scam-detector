import tkinter as tk
from engine import analyze

root = tk.Tk()
root.withdraw()
last = None          # last clipboard text we already checked
current = None       # the popup currently on screen


def popup(r):
    global current
    if current is not None:
        try:
            current.destroy()          # close the old popup first
        except tk.TclError:
            pass
    w = tk.Toplevel(root)
    current = w
    w.title("Scam Shield")
    w.attributes("-topmost", True)
    color = "#b91c1c" if r["verdict"] == "SCAM" else "#b45309"
    w.configure(bg=color)
    w.geometry("380x190+%d+%d" % (w.winfo_screenwidth() - 400, w.winfo_screenheight() - 260))
    head = "SCAM ALERT" if r["verdict"] == "SCAM" else "SUSPICIOUS MESSAGE"
    tk.Label(w, text=f"{head}  ({r['scam_percent']}%)", bg=color, fg="white",
             font=("Segoe UI", 14, "bold")).pack(pady=(14, 6))
    why = "\n".join("- " + x for x in r["reasons"][:3]) or "Looks like known scam wording"
    tk.Label(w, text=why, bg=color, fg="white", font=("Segoe UI", 10),
             justify="left", wraplength=340).pack()
    tk.Label(w, text="Do NOT click links or share OTP. Call 1930 if money lost.",
             bg=color, fg="white", font=("Segoe UI", 9, "italic"), wraplength=340).pack(pady=8)
    tk.Button(w, text="Close", command=w.destroy).pack()
    w.after(20000, lambda: w.winfo_exists() and w.destroy())


def poll():
    global last
    try:
        try:
            t = root.clipboard_get()
        except tk.TclError:
            t = ""
        # Only act when the clipboard text has CHANGED
        if t != last:
            last = t
            if len(t) > 15:
                r = analyze(t)
                print("Checked:", r["verdict"], r["scam_percent"], "%")
                if r["verdict"] == "SCAM":      # popup only for clear scams
                    popup(r)
    except Exception as e:
        print("Error (still running):", e)
    finally:
        root.after(1000, poll)


print("Scam Shield watcher running. Copy any message and I will check it. Ctrl+C to stop.")
poll()
root.mainloop()