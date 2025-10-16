import random

def first_bag (bag):
    ##取得第一包
    long_block=[]
    short_block=[]
    for i in range(len(bag)):
        if bag[i] == 'L' or bag[i] == 'O' or bag[i] == 'J':
            long_block.append(bag[i])
        elif bag[i] == 'T' or bag[i] == 'S' or bag[i] == 'Z':
            short_block.append(bag[i])
    return long_block,short_block

def direction (short_block):
    if short_block[0] == 'T' and short_block[1] == 'Z':
        return "right"
    elif short_block[0] == 'Z':
        return "right"
    elif short_block[0] == 'S':
        return "left"
    elif short_block[0] == 'T' and short_block[1] == 'S':
        return "left"

def open_derection (long_block,direction):
    if long_block == ['L','O','J']:
        return "left"
    elif long_block == ['J','O','L']:
        return "right"
    elif long_block == ['O','J','L']:
        return "down"
    elif long_block == ['O','L','J']:
        return "down"
    elif long_block == ['L','J','O']:
        if direction == "left":
            return "left"
        elif direction == "right":
            return "up"
    elif long_block == ['J','L','O']:
        if direction == "left":
            return "up"
        elif direction == "right":
            return "right"


def randomize_bag(bag, seed=None):
	"""回傳 bag 的隨機排列（不改變原 list）。若 seed 為 None 則隨機產生 seed。"""
	# 使用 SystemRandom 產生不可預測的 seed（但之後使用 Random(seed) 可重現該次順序）
	if seed is None:
		seed = random.SystemRandom().randint(0, 2**32 - 1)
	rng = random.Random(seed)
	new_bag = bag.copy()
	rng.shuffle(new_bag)
	return new_bag

bag=['I','O','T','S','Z','J','L']
new_bag=randomize_bag(bag)
(long_block, short_block)=first_bag(new_bag)
print("new_bag:", new_bag)
print("direction:",direction(short_block))
print("open_direction:",open_derection(long_block,direction(short_block)))
