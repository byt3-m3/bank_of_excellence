import random
import string
from dataclasses import dataclass


@dataclass
class PasswordPolicy:
    pass


@dataclass
class BasicPasswordPolicy:
    length: int = 1


@dataclass
class AdvancedPasswordPolicy:
    length: int = 1
    alphabets_count: int = 1
    digits_count: int = 1
    special_characters_count: int = 1
    upper_case_count: int = 1
    lower_case_count: int = 1


def make_basic_password_policy(length: int) -> BasicPasswordPolicy:
    return BasicPasswordPolicy(
        length=length
    )


def make_advanced_password_policy(
        length: int,
        alphabets_count: int,
        digits_count: int,
        special_characters_count: int,
        lower_case_count: int,
        upper_case_count: int

) -> AdvancedPasswordPolicy:
    return AdvancedPasswordPolicy(
        length=length,
        alphabets_count=alphabets_count,
        digits_count=digits_count,
        special_characters_count=special_characters_count,
        lower_case_count=lower_case_count,
        upper_case_count=upper_case_count,
    )


def generate_random_password_basic(password_policy: BasicPasswordPolicy):
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    random.shuffle(characters)

    password = []
    for i in range(password_policy.length):
        password.append(random.choice(characters))

    random.shuffle(password)

    return "".join(password)


def generate_random_password_advanced(password_policy: AdvancedPasswordPolicy):
    alphabets = list(string.ascii_letters)
    digits = list(string.digits)
    special_characters = list("!@#$%^&*()")
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    ## length of password from the user
    length = password_policy.length

    ## number of character types
    alphabets_count = password_policy.alphabets_count
    digits_count = password_policy.digits_count
    special_characters_count = password_policy.special_characters_count

    characters_count = alphabets_count + digits_count + special_characters_count

    ## check the total length with characters sum count
    ## print not valid if the sum is greater than length
    if characters_count > length:
        print("Characters total count is greater than the password length")
        return

    ## initializing the password
    password = []

    ## picking random alphabets
    for _ in range(alphabets_count):
        password.append(random.choice(alphabets))

    ## picking random digits
    for _ in range(digits_count):
        password.append(random.choice(digits))

    ## picking random alphabets
    for _ in range(special_characters_count):
        password.append(random.choice(special_characters))

    for _ in range(password_policy.upper_case_count):
        password.append(random.choice(string.ascii_uppercase))

    for _ in range(password_policy.lower_case_count):
        password.append(random.choice(string.ascii_lowercase))

    ## if the total characters count is less than the password length
    ## add random characters to make it equal to the length
    if characters_count < length:
        random.shuffle(characters)
        for _ in range(length - characters_count):
            password.append(random.choice(characters))

    ## shuffling the resultant password
    random.shuffle(password)

    ## converting the list to string
    ## printing the list
    return "".join(password)
