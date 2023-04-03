def multiple_line_input(with_left_strip: bool = False):
    print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line if not with_left_strip else line.lstrip())
    return "\n".join(contents)
