test_dict = {}
for i in range(10_000_000):
    test_dict[f'key{i}'] = f'value{i}'

print(len(test_dict))  # ได้ 1000000
