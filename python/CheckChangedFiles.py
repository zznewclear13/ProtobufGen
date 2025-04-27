import os
import json
import hashlib

def compute_hash(file_path):
    """计算文件的MD5哈希值"""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # 读取64KB的块
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except IOError:
        # 如果文件无法读取，视为已被删除或不可访问，返回空哈希
        return ''

def scanDirectory(directory, stateFile, extensions, force):
    # 获取当前目录下所有指定后缀文件的状态（不含哈希）
    currentFiles = {}
    for root, _, files in os.walk(directory):
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                path = os.path.join(root, f)
                relPath = os.path.relpath(path, directory)
                currentFiles[path] = {
                    "relPath": relPath,
                    "mtime": os.path.getmtime(path)
                }
    
    # 加载旧状态（如果存在）
    oldFiles = {}
    if (not force) and os.path.exists(stateFile):
        with open(stateFile, 'r') as f:
            oldFiles = json.load(f)
    
    modifiedFiles = []
    deletedFiles = []
    unchangedFiles = []
    
    # 处理当前文件，计算哈希并分类
    for path, currentData in currentFiles.items():
        currentData['hash'] = None  # 初始化哈希值
        if path in oldFiles:
            oldData = oldFiles[path]
            # 检查旧数据是否包含哈希
            if 'hash' not in oldData:
                # 旧状态无哈希，必须计算当前哈希并视为修改
                currentHash = compute_hash(path)
                currentData['hash'] = currentHash
                modifiedFiles.append({
                    "absPath": path,
                    "relPath": currentData['relPath'],
                    "mtime": currentData['mtime'],
                    "hash": currentHash
                })
            else:
                currentMtime = currentData['mtime']
                oldMtime = oldData['mtime']
                if currentMtime == oldMtime:
                    # mtime未变，复用旧哈希
                    currentData['hash'] = oldData['hash']
                    unchangedFiles.append({
                        "absPath": path,
                        "relPath": currentData['relPath'],
                        "mtime": currentData['mtime'],
                        "hash": oldData['hash']
                    })
                else:
                    # mtime变化，计算当前哈希
                    currentHash = compute_hash(path)
                    currentData['hash'] = currentHash
                    if currentHash != oldData['hash']:
                        modifiedFiles.append({
                            "absPath": path,
                            "relPath": currentData['relPath'],
                            "mtime": currentData['mtime'],
                            "hash": currentHash
                        })
                    else:
                        # 哈希相同，视为未变化
                        unchangedFiles.append({
                            "absPath": path,
                            "relPath": currentData['relPath'],
                            "mtime": currentData['mtime'],
                            "hash": currentHash
                        })
        else:
            # 新增文件，计算哈希并标记为修改
            currentHash = compute_hash(path)
            currentData['hash'] = currentHash
            modifiedFiles.append({
                "absPath": path,
                "relPath": currentData['relPath'],
                "mtime": currentData['mtime'],
                "hash": currentHash
            })
    
    # 检查被删除的文件
    for path, oldData in oldFiles.items():
        if path not in currentFiles:
            deletedFiles.append({
                "absPath": path,
                "relPath": oldData.get('relPath', ''),
                "mtime": oldData.get('mtime', 0),
                "hash": oldData.get('hash', '')
            })
    
    # 保存当前状态（包含哈希）
    with open(stateFile, 'w') as f:
        stateData = {}
        for path, data in currentFiles.items():
            stateData[path] = {
                'relPath': data['relPath'],
                'mtime': data['mtime'],
                'hash': data['hash']
            }
        json.dump(stateData, f)
    
    return modifiedFiles, deletedFiles, unchangedFiles