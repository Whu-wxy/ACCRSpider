
# name = '华山神庙碑 - 隶书 - “人”'
# name = name.strip().replace("“", "").replace("”", "")
# print(name)


import os
path = './imgs'

count = 0
cates = os.listdir(path)
for cate in cates:
    words = os.listdir(os.path.join(path, cate))
    for word in words:
        count += len(os.listdir(os.path.join(path, cate, word)))

print('sum: ', count)


