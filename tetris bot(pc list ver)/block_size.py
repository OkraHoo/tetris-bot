# 新增：棋盤尺寸常數
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# 使用 SRS 類型矩陣定義方塊（I:4x4, O:2x2, 其餘:3x3）
PIECES = {
    'I': [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'O': [
        [1,1],
        [1,1]
    ],
    'T': [
        [0,1,0],
        [1,1,1],
        [0,0,0]
    ],
    'S': [
        [0,1,1],
        [1,1,0],
        [0,0,0]
    ],
    'Z': [
        [1,1,0],
        [0,1,1],
        [0,0,0]
    ],
    'J': [
        [1,0,0],
        [1,1,1],
        [0,0,0]
    ],
    'L': [
        [0,0,1],
        [1,1,1],
        [0,0,0]
    ]
}

# 每個方塊在其矩陣內的旋轉中心（row, col），可為浮點數以接近 SRS 原點
# I 在 4x4 中常以 (1.5,1.5) 為中心，O 以 (0.5,0.5)，其餘以 (1,1)
PIECE_CENTERS = {
    'I': (1.5, 1.5),
    'O': (0.5, 0.5),
    'T': (1.0, 1.0),
    'S': (1.0, 1.0),
    'Z': (1.0, 1.0),
    'J': (1.0, 1.0),
    'L': (1.0, 1.0)
}

# 新增：旋轉工具與預先計算的旋轉矩陣（0..3）
def rotate90(matrix):
	"""順時針 90° 旋轉方陣（可處理矩陣）"""
	rows = len(matrix)
	cols = len(matrix[0])
	# 轉置並反轉列以獲得順時針旋轉
	return [[matrix[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]

def canonicalize(piece_matrix, size):
	"""把矩陣 padding/crop 成 size x size（保留原值，其餘補 0）"""
	rows = len(piece_matrix)
	cols = len(piece_matrix[0])
	# 每列補齊到 size 長度
	new = [row + [0] * (size - cols) for row in piece_matrix]
	# 若列數不足則補零列
	for _ in range(size - rows):
		new.append([0] * size)
	return new

def _size_for_piece(name):
	"""I->4, O->2, 其餘->3"""
	if name == 'I':
		return 4
	if name == 'O':
		return 2
	return 3

# 預先計算每個方塊的 4 個旋轉狀態（0..3）
PIECE_ROTATIONS = {}
for name, mat in PIECES.items():
	size = _size_for_piece(name)
	cur = canonicalize(mat, size)
	rots = []
	for _ in range(4):
		rots.append(cur)
		cur = rotate90(cur)
	PIECE_ROTATIONS[name] = rots

def get_rotations(name):
	"""回傳指定方塊的 4 個旋轉矩陣（index 0..3），若不存在回傳 None"""
	return PIECE_ROTATIONS.get(name)
