SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def subscript(text):
    return text.translate(SUB)


def supscript(text):
    return text.translate(SUP)


def spaces(num):
    # Wrapper for creating blankspace
    return " " * num


if __name__ == "__main__":
    user_num = input("Give me a number:\n")
    print("User number: {:d}".format(int(user_num)))
    print("Superscript: {}".format(supscript(user_num)))
    print("Subscript: {}".format(subscript(user_num)))
