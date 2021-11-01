import random


# Fisher–Yates Shuffle Algorithm
def shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]


def allocate(participants):
    def is_valid(participant, recipient):
        return participant["name"] != recipient["name"] and recipient["name"] not in participant["exclusions"]

    recipients = list(participants)
    while not all(is_valid(*pair) for pair in zip(participants, recipients)):
        shuffle(recipients)

    return list(zip(participants, recipients))
