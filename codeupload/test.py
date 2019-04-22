data = [{'user_id': 3, 'user': 'wori', 'i': 362}, {'user_id': 1, 'user': 'aki', 'i': 3653}, {'user_id': 2, 'user': 'desky', 'i': 3005}]
h = 0
for k in data:
    if k['i'] > h:
        h = k['i']
print(h)
for k in data:
    if k['i'] == 3653:
        print(k['user'])

