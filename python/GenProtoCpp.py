import os
import sys
import argparse
import traceback
import shutil
import subprocess
import re
from jinja2 import Environment, FileSystemLoader

import CheckChangedFiles

basicProtoTypes = {'int32', 'float', 'string', 'uint64', 'bool'}

def cleanGeneratedDir(generatedDir, wrapperDir):
    """清空Generated和Wrapper目录"""
    for dir in [generatedDir, wrapperDir]:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir, exist_ok=True)

def parseProtoType(rawType):
    """统一类型处理逻辑"""
    if rawType.endswith('Proto'):
        return rawType[:-5]
    return rawType

def parseProtoFile(protoPath):
    """解析proto文件元数据（修复返回值结构）"""
    with open(protoPath, 'r') as f:
        content = f.read()

    # 提取消息名称
    messageMatch = re.search(r'message\s+(\w+)\s*{', content)
    if not messageMatch:
        return None
    
    protoClassName = messageMatch.group(1)
    sourceClassName = protoClassName[:-5] if protoClassName.endswith('Proto') else protoClassName

    # 优化字段解析正则
    fieldRegex = re.compile(
        r'^\s*'
        r'(?:(repeated)\s+)?'  # 重复标记
        r'(?:map\s*<\s*([\w.]+)\s*,\s*([\w.]+)\s*>|([\w.]+))'  # 类型
        r'\s+(\w+)\s*=\s*\d+;',  # 字段名
        re.MULTILINE
    )

    propertyInfos = []
    parentInfo = {'protoName': None, 'sourceName': None}
    
    for match in fieldRegex.finditer(content):
        isRepeated, mapKey, mapVal, singleType, fieldName = match.groups()
        
        if fieldName == 'parent':
            parentType = parseProtoType(mapVal or singleType)
            parentInfo = {
                'protoName': mapVal or singleType,
                'sourceName': parentType if parentType in basicProtoTypes else parentType
            }
            continue

        # 构建字段信息
        fieldInfo = {
            'name': fieldName,
            'isRepeated': bool(isRepeated),
            'isMap': bool(mapKey)
        }

        if fieldInfo['isMap']:
            fieldInfo.update({
                'keyType': mapKey,
                'valueType': parseProtoType(mapVal),
                'isBasic': mapVal in basicProtoTypes
            })
        else:
            fieldType = parseProtoType(singleType)
            fieldInfo.update({
                'valueType': fieldType,
                'isBasic': fieldType in basicProtoTypes
            })

        propertyInfos.append(fieldInfo)

    return {
        'protoClassName': protoClassName,
        'sourceClassName': sourceClassName,  # 确保包含这个key
        'propertyInfos': propertyInfos,
        'protoParentName': parentInfo['protoName'],  # 修正key名称
        'sourceParentName': parentInfo['sourceName']
    }

def generateWrapperFiles(protoFileInfo, templateDir, wrapperDir, assetPrefix, generatedPrefix):
    """生成包装文件（完整修复版本）"""
    protoAbsPath = protoFileInfo['absPath']
    protoRelPath = protoFileInfo['relPath']
    
    # 解析proto文件
    parsedInfo = parseProtoFile(protoAbsPath)
    if not parsedInfo:
        print(f"Failed to parse {protoRelPath}")
        return False

    # 构建上下文数据
    context = {
        'sourceClassName': parsedInfo['sourceClassName'],
        'protoClassName': parsedInfo['protoClassName'],
        'propertyInfos': parsedInfo['propertyInfos'],
        'sourceParentName': parsedInfo['sourceParentName'],
        'sourceHeaderFile': os.path.join(assetPrefix, protoRelPath.replace('.proto', '.h')).replace('\\', '/'),
        'protoHeaderFile': os.path.join(generatedPrefix, protoRelPath.replace('.proto', '.pb.h')).replace('\\', '/'),
        'wrapperHeaderFile': f"{parsedInfo['sourceClassName']}.wrapper.h"
    }

    # 渲染模板
    env = Environment(loader=FileSystemLoader(templateDir),
                        trim_blocks=True,     # 移除标签后的换行
                        lstrip_blocks=True,   # 移除标签前的空格
                        )
    try:
        hContent = env.get_template('wrapper.h.template').render(context)
        cppContent = env.get_template('wrapper.cpp.template').render(context)
        
        # 构建输出路径
        baseName = os.path.splitext(protoRelPath)[0]  # 保留目录结构 如"School/Teacher"
        basePath = os.path.join(wrapperDir, baseName)
        
        # 确保目录存在
        outputDir = os.path.dirname(basePath)
        os.makedirs(outputDir, exist_ok=True)
        
        # 写入文件
        for ext, content in [('.h', hContent), ('.cpp', cppContent)]:
            with open(f"{basePath}.wrapper{ext}", 'w', encoding='utf-8') as f:
                f.write(content)
        
        return True
    except Exception as e:
        print(f"Generate failed: {protoRelPath} - {str(e)}")
        return False

def compileProto(protoFileInfo, protocPath, protosDir, generatedDir):
    """编译proto文件（优化错误处理）"""
    try:
        result = subprocess.run([
            protocPath,
            f"--cpp_out={generatedDir}",
            f"--proto_path={protosDir}",
            protoFileInfo['absPath']
        ], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Protoc error: {getattr(e, 'stderr', str(e))}")
        return False

def deleteGeneratedFiles(protoFile, generatedDir, wrapperDir):
    """删除生成的文件"""
    baseName = os.path.splitext(protoFileInfo['relPath'])[0]
    deleted = False

    # 删除协议生成文件
    for dirPath, ext in [(generatedDir, '.pb.h'), (generatedDir, '.pb.cc'),
                         (wrapperDir, '.wrapper.h'), (wrapperDir, '.wrapper.cpp')]:
        filePath = os.path.join(dirPath, f"{baseName}{ext}")
        if os.path.exists(filePath):
            os.remove(filePath)
            deleted = True
            
    return deleted

def main(args):
    try:
        protosDir = args.protobuf_gen_proto_folder
        generatedDir = args.protobuf_gen_generated_folder
        wrapperDir = args.protobuf_gen_wrapper_folder
        templateDir = args.protobuf_gen_wrapper_template
        protocPath = args.protobuf_gen_executive_path
        assetFolder = args.protobuf_gen_asset_folder
        sourceFolder = args.protobuf_gen_source_folder
        stateFile = args.protobuf_gen_state_file
        force = args.protobuf_gen_force_override

        assetPrefix = os.path.relpath(assetFolder, sourceFolder)
        generatedPrefix = os.path.relpath(generatedDir, sourceFolder)

        if force:
            cleanGeneratedDir(generatedDir, wrapperDir)

        modifiedProtoFiles, deletedProtoFiles, unchangedProtoFiles = CheckChangedFiles.scanDirectory(
            protosDir, stateFile, ['.proto'], force)

        successCount = 0
        failureCount = 0
        for proto in modifiedProtoFiles:
            # 先解析proto文件
            parsedInfo = parseProtoFile(proto['absPath'])
            if not parsedInfo:
                print(f"Failed to parse {proto['relPath']}")
                failureCount += 1
                continue
                
            # 合并文件信息
            fullInfo = {**proto, **parsedInfo}
            if (compileProto(fullInfo, protocPath, protosDir, generatedDir) 
                and generateWrapperFiles(fullInfo, templateDir, wrapperDir, 
                                       os.path.relpath(assetFolder, sourceFolder), 
                                       os.path.relpath(generatedDir, sourceFolder))):
                successCount += 1
            else:
                failureCount += 1

        deletedCount = 0
        for proto in deletedProtoFiles:
            if deleteGeneratedFiles(proto, generatedDir, wrapperDir):
                deletedCount += 1

        sys.stdout.write(
            f"GenProto.py finished!\n"
            f"Modified: {successCount} (failed: {failureCount}), "
            f"Deleted: {deletedCount}, "
            f"Unchanged: {len(unchangedProtoFiles)}\n"
        )
        return 0 if failureCount == 0 else 1
    except Exception as e:
        sys.stderr.write(''.join(traceback.format_exception(e)).strip())
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-exe", "--protobuf-gen-executive-path", required=True)
    parser.add_argument("-proto", "--protobuf-gen-proto-folder", required=True)
    parser.add_argument("-generated", "--protobuf-gen-generated-folder", required=True)
    parser.add_argument("-wrapper", "--protobuf-gen-wrapper-folder", required=True)
    parser.add_argument("-template", "--protobuf-gen-wrapper-template", required=True)
    parser.add_argument("-asset", "--protobuf-gen-asset-folder", required=True)
    parser.add_argument("-source", "--protobuf-gen-source-folder", required=True)
    parser.add_argument("-state", "--protobuf-gen-state-file", required=True)
    parser.add_argument("-force", "--protobuf-gen-force-override", action="store_true")
    
    args = parser.parse_args()
    sys.exit(main(args))