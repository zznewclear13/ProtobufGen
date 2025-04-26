import os
import json

def scanDirectory(directory, stateFile, extensions, force):
    '''
    检测目录下文件的变化，返回三个列表：
    1. 新增或修改的文件列表
    2. 被删除的文件列表
    3. 未变化的文件列表
    
    参数:
        directory: 要扫描的目录
        stateFile: 存储文件状态的文件路径
        extensions: 要检测的文件后缀名列表
        force: 是否强制重新扫描所有文件
    
    返回:
        (modifiedFiles, deletedFiles, unchangedFiles)
    '''
    # 获取当前目录下所有指定后缀文件的状态
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
    
    # 保存当前状态
    with open(stateFile, 'w') as f:
        json.dump(currentFiles, f)
    
    # 找出新增或修改的文件
    modifiedFiles = [
        {"absPath": path, "relPath": data["relPath"], "mtime": data["mtime"]}
        for path, data in currentFiles.items()
        if path not in oldFiles or data != oldFiles.get(path)
    ]
    
    # 找出被删除的文件（在旧状态中存在但在当前状态中不存在）
    deletedFiles = [
        {"absPath": path, "relPath": data["relPath"], "mtime": data["mtime"]}
        for path, data in oldFiles.items()
        if path not in currentFiles
    ]
    
    # 找出未变化的文件
    unchangedFiles = [
        {"absPath": path, "relPath": data["relPath"], "mtime": data["mtime"]}
        for path, data in currentFiles.items()
        if path in oldFiles and data == oldFiles.get(path)
    ]
    
    return modifiedFiles, deletedFiles, unchangedFiles