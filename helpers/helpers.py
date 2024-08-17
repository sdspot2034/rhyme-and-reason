def get_url(x,height=640):
    for elem in x:
        if elem['height'] == height: return elem['url']
    return None