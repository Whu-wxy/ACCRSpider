# 开始爬取的网址
base_url = "https://shufa.supfree.net/raky.asp?zi="

# 图片存储路径，如果不存在，将会创建文件夹
# 将会在这个文件夹下为每个网页创建一个子文件夹存图片
save_path = './imgs/'

#下载图片线程数
thread_num = 4


# 下载图片的最小KB值
img_size_threld = 0      # KB