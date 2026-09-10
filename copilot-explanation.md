Tkinter is Python’s standard GUI library. Here, it creates a window containing a settings form.

## Main objects

```python
root = tk.Tk()
SettingsEditor(root)
root.mainloop()
```

- `tk.Tk()` creates the main application window.
- `SettingsEditor(root)` builds the interface inside it.
- `mainloop()` keeps the window open and listens for events such as clicks and typing.

## `tk` versus `ttk`

```python
import tkinter as tk
from tkinter import ttk
```

- `tk` provides the original Tkinter widgets: `Tk`, `Canvas`, `StringVar`.
- `ttk` provides themed widgets: `Frame`, `Label`, `Entry`, `Button`, `Scrollbar`.

`ttk` widgets generally look more modern and adapt better to the operating system theme.

## What is `ttk.Frame`?

A `Frame` is an invisible container used to group widgets.

For example:

```python
main = ttk.Frame(master, padding=12)
main.pack(fill="both", expand=True)
```

`main` groups the whole interface.

Later:

```python
row = ttk.Frame(self.form_frame, padding=(0, 4))
```

Each `row` groups one setting:

```text
[label] [entry] [Parcourir]
```

And:

```python
actions = ttk.Frame(main)
```

groups the action buttons at the bottom.

Frames make it possible to organize the window hierarchically:

```text
root
└── main
    ├── title
    ├── canvas
    │   └── form_frame
    │       ├── row
    │       ├── row
    │       └── row
    └── actions
```

## `padding`

```python
ttk.Frame(master, padding=12)
```

`padding` creates internal space between the frame's border and its children.

A value of `12` means:

```text
12 pixels on every side
```

This:

```python
padding=(0, 4)
```

means:

```text
left = 0, right = 0, top = 4, bottom = 4
```

So every settings row gets 4 pixels of vertical breathing room.

## `pack`

`pack()` is a geometry manager. It decides where widgets are placed.

### `fill`

```python
main.pack(fill="both")
```

Allows the widget to stretch:

- `"x"`: horizontally
- `"y"`: vertically
- `"both"`: horizontally and vertically
- omitted: do not stretch

### `expand`

```python
main.pack(fill="both", expand=True)
```

`expand=True` tells Tkinter to give the widget any extra space available in the window.

Without it, `main` would normally remain close to its requested size. With it, `main` fills the window when the user resizes it.

A useful distinction:

- `fill` controls how the widget uses space assigned to it.
- `expand` controls whether it receives extra available space.

### `side`

```python
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
```

- `side="left"` places the canvas on the left.
- `side="right"` places the scrollbar on the right.
- The canvas expands to occupy the remaining space.
- The scrollbar stretches vertically.

### `anchor`

```python
canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
```

`anchor="nw"` means the top-left corner of `form_frame` is placed at coordinate `(0, 0)` inside the canvas.

`nw` means “north-west”, or top-left.

## `padx` and `pady`

These are external margins added when placing a widget.

```python
entry.pack(side="left", fill="x", expand=True, padx=(40, 6))
```

Here:

```python
padx=(40, 6)
```

means:

- 40 pixels on the left
- 6 pixels on the right

This creates space between the label and entry, and a smaller space between the entry and the button.

Similarly:

```python
title.pack(anchor="w", pady=(0, 10))
```

means:

- no extra space above the title
- 10 pixels below it

So `pady=(0, 10)` separates the title from the form.

The difference is:

```python
padding=12
```

is usually internal space inside a widget or frame.

```python
padx=...
pady=...
```

are margins around a widget when it is positioned with `pack`.

## The scrollable form

This part creates a scrollable area:

```python
canvas = tk.Canvas(main, highlightthickness=0)
scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
```

The `Canvas` can display content larger than the visible area. The `Scrollbar` controls its vertical position.

```python
canvas.configure(yscrollcommand=scrollbar.set)
```

This connects the canvas back to the scrollbar. When the canvas moves, the scrollbar thumb is updated.

The connection is bidirectional:

```text
Scrollbar -> canvas.yview()
Canvas movement -> scrollbar.set()
```

### Why `command=canvas.yview`?

`command` expects a function to call when the scrollbar is moved.

```python
command=canvas.yview
```

passes the function itself.

It does not execute it immediately. This would be wrong:

```python
command=canvas.yview()
```

because that calls the function during interface creation.

Tkinter later calls it with the necessary arguments, such as `"moveto"` or `"scroll"`.

## Why put a `Frame` inside a `Canvas`?

A canvas is good for scrolling, but it does not automatically arrange form widgets. A frame is good for arranging widgets, but it does not scroll by itself.

Therefore, the code combines them:

```python
self.form_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
```

The frame contains all the rows, while the canvas provides scrolling.

This binding updates the scrollable area whenever the frame changes size:

```python
self.form_frame.bind(
    "<Configure>",
    lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
)
```

`canvas.bbox("all")` calculates the bounding box of everything inside the canvas. Without updating `scrollregion`, the scrollbar would not know how far it can scroll.

## `command` on buttons

```python
ttk.Button(actions, text="Générer", command=self.generate)
```

When the button is clicked, Tkinter calls:

```python
self.generate()
```

Again, the function is passed without parentheses:

```python
command=self.generate
```

This would execute too early:

```python
command=self.generate()
```

The browse buttons use a lambda because they need to pass arguments:

```python
command=lambda n=name, v=var: self.choose_file(n, v)
```

When clicked, this calls:

```python
self.choose_file(name, var)
```

The lambda also captures the current loop values of `name` and `var`.

## A typical row

```python
row = ttk.Frame(self.form_frame, padding=(0, 4))
row.pack(fill="x")

label = ttk.Label(row, text=...)
label.pack(side="left")

entry = ttk.Entry(row, textvariable=var)
entry.pack(side="left", fill="x", expand=True, padx=(40, 6))
```

This creates:

1. A row frame with vertical padding.
2. A label on the left.
3. An entry beside it.
4. The entry expands horizontally.
5. Optional button after the entry.

The result is approximately:

```text
Description                         [file path................] [Parcourir]
```

## `StringVar`

```python
var = tk.StringVar(value=str(value))
entry = ttk.Entry(row, textvariable=var)
```

`StringVar` is a Tkinter-managed variable connected to the entry.

Reading:

```python
value = var.get()
```

Updating:

```python
var.set(filename)
```

automatically updates the text displayed in the entry. This is why `choose_file()` can update the field without directly manipulating the `Entry` widget.