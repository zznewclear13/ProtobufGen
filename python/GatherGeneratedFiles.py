import os
import sys
import argparse
import traceback
from pathlib import Path

def getRelativePaths(basePath, folder, extensions):
    basePath = Path(basePath).absolute()
    folder = Path(folder).absolute()
    
    collectedFiles = []
    for root, _, files in os.walk(folder):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                fullPath = Path(root) / file
                relPath = os.path.relpath(fullPath, basePath)
                collectedFiles.append(relPath.replace('\\', '/'))  # 统一正斜杠
    
    return collectedFiles

def generateAllWrappersHeader(wrapperFiles, outputPath, basePath):
    try:
        # 按目录深度和字母顺序排序
        sortedFiles = sorted(
            wrapperFiles,
            key=lambda x: (x.count('/'), x)  # 先按目录深度，再按字母顺序
        )
        
        # 生成头文件内容
        content = ['#pragma once\n']
        content.extend(f'#include "{path}"' for path in sortedFiles)
        
        # 确保输出目录存在
        outputPath = Path(outputPath)
        outputPath.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(outputPath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
            
        return True
    except Exception as e:
        print(f"Error generating all wrappers header: {str(e)}")
        return False

def main(args):
    try:
        basePath = Path(args.protobuf_gen_base_path).absolute()
        generatedFolder = Path(args.protobuf_gen_generated_folder).absolute()
        wrapperFolder = Path(args.protobuf_gen_wrapper_folder).absolute()
        allWrappersPath = Path(args.protobuf_gen_all_wrappers).absolute() 

        # 收集源文件列表
        generatedFiles = getRelativePaths(basePath, generatedFolder, ['.h', '.cc'])
        wrapperFiles = getRelativePaths(basePath, wrapperFolder, ['.h', '.cpp'])
        
        # 生成聚合头文件
        wrapperHFiles = getRelativePaths(basePath, wrapperFolder, ['.h'])
        if not generateAllWrappersHeader(wrapperHFiles, allWrappersPath, basePath):
            return 1

        # 合并输出结果
        all_files = generatedFiles + wrapperFiles
        sys.stdout.write(';'.join(all_files))
        return 0
    
    except Exception as e:
        sys.stderr.write(''.join(traceback.format_exception(e)).strip())
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-base", "--protobuf-gen-base-path", type=str, required=True)
    parser.add_argument("-generated", "--protobuf-gen-generated-folder", type=str, required=True)
    parser.add_argument("-wrapper", "--protobuf-gen-wrapper-folder", type=str, required=True)
    parser.add_argument("-all-wrappers", "--protobuf-gen-all-wrappers", type=str, required=True)
    args = parser.parse_args()

    sys.exit(main(args))