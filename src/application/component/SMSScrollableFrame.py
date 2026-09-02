# @see https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame

from tkinter import Frame, Scrollbar, Canvas

from src.domain.entity.Theme import Theme


class SMSScrollableFrame(Frame):
    """Vertically scrolling area that fills whatever room its parent gives it."""

    def __init__(self, container, theme: Theme):
        super().__init__(master=container, bg=theme.background)
        self.theme = theme

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.create_scrollable_frame()

    def get_interior(self) -> Frame:
        return self.interior

    def reload(self):
        for child in list(self.children.values()):
            child.destroy()
        self.create_scrollable_frame()

    def create_scrollable_frame(self):
        vscrollbar = Scrollbar(
            self,
            orient="vertical",
            background=self.theme.surface,
            troughcolor=self.theme.background,
            activebackground=self.theme.accent,
            borderwidth=0,
            highlightthickness=0,
        )
        vscrollbar.grid(sticky='ns', row=0, column=1)

        canvas = Canvas(
            self,
            highlightthickness=0,
            yscrollcommand=vscrollbar.set,
            bg=self.theme.background,
        )
        canvas.grid(sticky='nsew', row=0, column=0)
        vscrollbar.config(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = Frame(canvas, bg=self.theme.background)
        self.interior.columnconfigure(0, weight=1)
        interior_id = canvas.create_window(0, 0, window=self.interior, anchor="nw")

        def __configure_interior(event):
            canvas.config(scrollregion=(0, 0, self.interior.winfo_reqwidth(), self.interior.winfo_reqheight()))

        self.interior.bind('<Configure>', __configure_interior)

        def __configure_canvas(event):
            # The interior always spans the canvas, so the cards inside it can stretch.
            canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', __configure_canvas)

        self.__bind_mouse_wheel(canvas)

    def __bind_mouse_wheel(self, canvas):
        """Scroll with the wheel only while the pointer is over this frame."""
        def on_wheel(event):
            direction = -1 if event.num == 4 or getattr(event, "delta", 0) > 0 else 1
            canvas.yview_scroll(direction, "units")

        def bind_wheel(event):
            for sequence in ('<Button-4>', '<Button-5>', '<MouseWheel>'):
                canvas.bind_all(sequence, on_wheel)

        def unbind_wheel(event):
            for sequence in ('<Button-4>', '<Button-5>', '<MouseWheel>'):
                canvas.unbind_all(sequence)

        canvas.bind('<Enter>', bind_wheel, add="+")
        canvas.bind('<Leave>', unbind_wheel, add="+")
