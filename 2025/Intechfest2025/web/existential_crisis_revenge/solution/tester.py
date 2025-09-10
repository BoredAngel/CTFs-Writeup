
import string
# from context import CONTEXT as context


not_in_any_emojis= [
        "e",
        "f",
        "h",
        "O",
        "P",
        "Q",
        "S",
        "0",
        "5",
        "8",
        "*",
        "-",
        ":",
        "_",
        "a",
        "j",
        "k",
        "m",
        "n",
        "p",
        "u",
        "w",
        "b",
        "i",
        "k",
        "l",
        "n",
        "q",
        "w",
        "H",
        "K",
        "L",
        "U",
        "W",
        "3",
        "4",
        "6",
        "7",
        "$",
        ")",
        "a",
        "d",
        "n",
        "o",
        "v",
        "w",
        "A",
        "B",
        "D",
        "E",
        "F",
        "z",
        "9",
        "!",
        "c",
        "C",
        "I",
        "J",
        "M",
        "2",
        "(",
        ",",
        "c",
        "I",
        "J",
        "M",
        "V",
        "Z",
        "1",
        "!",
        "c",
        "J",
        "M",
        "N",
        "V",
        "Z",
        "9",
        ",",
        "s",
        "I",
        "Z",
        "1",
        "(",
        "c",
        "s",
        "C",
        "M",
        "Z",
        "1",
        "!",
        "(",
        "c",
        "s",
        "I",
        "J",
        "M",
        "N",
        "9",
        "!",
        "M",
        "V",
        "!",
        "(",
        ",",
        "z",
        "I",
        "J",
        "N",
        "Z",
        "!",
        ",",
        "z",
        "I",
        "J",
        "M",
        "N",
        "V",
        "9",
        "!",
        ",",
        "z",
        "C",
        "J",
        "(",
        "c",
        "C",
        "J",
        "M",
        "("
    ]

not_not_in_any_emojis = ['g', 'r', 't', 'x', 'y', 'G', 'R', 'T', 'X', 'Y', "'", '+', '.']

allchar = list(string.ascii_letters + string.digits + "!$'()*+,-.:_")

remaining_char = []
for char in allchar:
    if char not in not_in_any_emojis:
        remaining_char.append(char)

print(remaining_char)

# @app.route("/xss_test", methods=["GET"])
# def xss_test():
#     q = request.args.get("cok")
#     return render_template_string("""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>XSS Test</title>
# </head>
# <body>
#     {{ xss | safe }}
# </body>
# </html>""", xss=q)