def count_vowels(string_to_check: str):
    return sum(1 for char in string_to_check if char in 'auoyei')


string = 'papao'
rez = count_vowels(string)
print(rez)