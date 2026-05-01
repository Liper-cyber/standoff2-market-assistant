import tkinter as tk

from .app import MenuApp


def main():
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
