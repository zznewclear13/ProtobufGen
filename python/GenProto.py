import os
import sys
import argparse
import traceback
import re
import shutil

import CheckChangedFiles

protoTypeMapping = {
    "PROTO_FLOAT": "float",
    "PROTO_INT": "int32",
    "PROTO_SIZE_T": "uint64",
    "PROTO_STRING": "string",
    "PROTO_VECTOR": "repeated",
    "PROTO_MAP": "map",
    "PROTO_TYPE": "message"
}

def parseProtoType(typeStr):
    """统一处理类型转换"""
    if typeStr.startswith("PROTO_TYPE("):
        return f"{typeStr[11:-1]}Proto"
    return protoTypeMapping.get(typeStr, f"{typeStr}Proto")

def parseProtoField(line):
    line = line.split("//")[0].strip()
    if not line or line.startswith("#"):
        return None

    # 使用正则表达式精确提取宏名称和字段名
    macroMatch = re.match(r'^(PROTO_\w+\([^)]+\)|PROTO_\w+)\s+([^\s;{]+)', line)
    if not macroMatch:
        return None

    protoMacro, fieldName = macroMatch.groups()

    # 处理vector类型
    if protoMacro.startswith("PROTO_VECTOR("):
        innerType = protoMacro[13:-1]
        protoType = f"repeated {parseProtoType(innerType)}"
    
    # 处理map类型（重构后）
    elif protoMacro.startswith("PROTO_MAP("):
        mapContent = protoMacro[10:-1].strip()
        keyType, _, valueType = mapContent.partition(',')
        keyType = keyType.strip()
        valueType = valueType.strip()

        if keyType not in ["PROTO_INT", "PROTO_STRING"]:
            return None

        protoType = f"map<{parseProtoType(keyType)}, {parseProtoType(valueType)}>"
    
    # 处理用户自定义类型
    elif protoMacro.startswith("PROTO_TYPE("):
        protoType = parseProtoType(protoMacro[11:-1])
    
    # 处理基本类型
    else:
        protoType = parseProtoType(protoMacro)

    return (protoType, fieldName) if protoType else None

def parseProtoProperties(headerPath, baseIncludePath, sourcePath, protosDir):
    """
    从.h文件中提取：
    1. PROTO_PROPERTY区域的字段
    2. PROTO_INCLUDE的依赖关系
    3. PROTO_PARENT指定的父类名称
    返回 (字段列表, 依赖列表, 父类名称, 解析状态)
    """
    protoFields = []
    protoIncludes = []
    parentClass = None
    inProtoSection = False
    hasParsingError = False
    
    with open(headerPath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # 提取PROTO_INCLUDE
            if "#include PROTO_INCLUDE(" in line:
                # 提取括号内的路径
                includePath = line.split("PROTO_INCLUDE(")[1].split(")")[0]
                # 转换为绝对路径
                absIncludePath = os.path.normpath(os.path.join(baseIncludePath, includePath))
                # 转换为相对于baseIncludePath的路径
                relIncludePath = os.path.relpath(absIncludePath, sourcePath)
                # 转换为.proto路径
                protoPath = os.path.splitext(relIncludePath)[0] + ".proto"
                protoIncludes.append(protoPath)

            # 提取PROTO_PARENT信息
            if line.startswith("class ") and "PROTO_PARENT" in line:
                # 匹配类似 PROTO_PARENT(EntityAsset) 的结构
                match = re.search(r'PROTO_PARENT\((\w+)\)', line)
                if match:
                    parentClass = match.group(1)
                
            # 处理PROTO_PROPERTY区域
            if "PROTO_PROPERTY_START" in line:
                inProtoSection = True
                continue
            elif "PROTO_PROPERTY_END" in line:
                break
                
            if not inProtoSection or not line:
                continue
                
            originalLine = line
            field = parseProtoField(line)
            if field:
                protoFields.append(field)
            else:  # 如果解析失败且包含PROTO_MAP
                print(f"Error: Failed to parse line: {originalLine}")
                hasParsingError = True
    
    return protoFields, protoIncludes, parentClass, hasParsingError

def generateProtoContent(protoFields, protoIncludes, parentClass, sourceHeader, protosDir, baseIncludePath):
    """生成带import的proto内容"""
    lines = [
        'syntax = "proto3";',
        f'// Auto-generated from {os.path.basename(sourceHeader)}',
        ''
    ]
    
    # 获取当前proto文件的相对路径
    currentProtoRelPath = os.path.splitext(os.path.relpath(sourceHeader, baseIncludePath))[0] + ".proto"
    currentProtoDir = os.path.dirname(currentProtoRelPath)
    
    # 添加import语句
    for include in protoIncludes:
        # 确保使用正斜杠
        relPath = include.replace('\\', '/')
        lines.append(f'import "{relPath}";')
    
    # 添加message定义
    messageName = os.path.splitext(os.path.basename(sourceHeader))[0]
    lines.append(f'message {messageName}Proto {{')

    # 添加父类字段
    if parentClass:
        lines.append(f'  {parentClass}Proto parent = 1;')  # 固定为第一个字段
    
    # 调整字段编号：如果存在父类，从2开始；否则从1开始
    fieldNumber = 2 if parentClass else 1
    for fieldType, fieldName in protoFields:
        lines.append(f'  {fieldType} {fieldName} = {fieldNumber};')
        fieldNumber += 1
    
    lines.append('}')
    return '\n'.join(lines)

def generateProtos(assetFolder, targetFolder, fileInfo, baseIncludePath):
    try:
        protoRelPath = os.path.splitext(fileInfo["relPath"])[0] + ".proto"
        protoAbsPath = os.path.join(targetFolder, protoRelPath)
        
        os.makedirs(os.path.dirname(protoAbsPath), exist_ok=True)
        
        # 获取字段和依赖关系
        protoFields, protoIncludes, parentClass, hasParsingError = parseProtoProperties(
            fileInfo["absPath"], 
            baseIncludePath,
            assetFolder,
            targetFolder
        )
        
        # 检查是否有解析错误
        if hasParsingError:
            print(f"Error: Failed to parse {fileInfo['absPath']}, skipping generation due to parsing errors")
            return False
            

        # 生成proto内容
        protoContent = generateProtoContent(
            protoFields=protoFields,
            protoIncludes=protoIncludes,
            parentClass=parentClass,
            sourceHeader=fileInfo["absPath"],
            protosDir=targetFolder,
            baseIncludePath=baseIncludePath
        )
        
        with open(protoAbsPath, 'w') as f:
            f.write(protoContent)
        
        print(f"Generated: {protoAbsPath}")
        return True
        
    except Exception as e:
        print(f"Error generating proto for {fileInfo['absPath']}: {str(e)}")
        return False

def deleteProtoFile(sourceHeaderPath, protoFolder, baseIncludePath):
    """删除与头文件对应的proto文件"""
    try:
        # 计算proto文件路径
        relPath = os.path.relpath(sourceHeaderPath, baseIncludePath)
        protoRelPath = os.path.splitext(relPath)[0] + ".proto"
        protoAbsPath = os.path.join(protoFolder, protoRelPath)
        
        if os.path.exists(protoAbsPath):
            os.remove(protoAbsPath)
            print(f"Deleted: {protoAbsPath}")
            return True
        return False
    except Exception as e:
        print(f"Error deleting proto file for {sourceHeaderPath}: {str(e)}")
        return False

def cleanGeneratedDir(protoFolder):
    """清空Protos目录"""
    if os.path.exists(protoFolder):
        shutil.rmtree(protoFolder)
    os.makedirs(protoFolder, exist_ok=True)

def main(args):
    try:
        baseIncludePath = args.protobuf_gen_base_include
        assetFolder = args.protobuf_gen_asset_folder
        protoFolder = args.protobuf_gen_proto_folder
        stateFile = args.protobuf_gen_state_file
        force = args.protobuf_gen_force_override
        
        # 如果是force模式，清空目标文件夹
        if force:
            print("Force mode: cleaning generated directory...")
            cleanGeneratedDir(protoFolder)
        
        # 获取变化的文件
        modifiedFiles, deletedFiles, unchangedFiles = CheckChangedFiles.scanDirectory(
            assetFolder, stateFile, ['.h'], force)
        
        # 处理新增和修改的文件
        successCount = 0
        failureCount = 0
        for file in modifiedFiles:
            if generateProtos(assetFolder, protoFolder, file, baseIncludePath):
                successCount += 1
            else:
                failureCount += 1
        
        # 处理删除的文件
        deletedCount = 0
        for file in deletedFiles:
            if deleteProtoFile(file["absPath"], protoFolder, baseIncludePath):
                deletedCount += 1
        
        # 输出统计信息
        sys.stdout.write(
            f"GenProto.py finished!\n"
            f"Modified: {successCount} (failed: {failureCount}), "
            f"Deleted: {deletedCount}, "
            f"Unchanged: {len(unchangedFiles)}\n"
        )
        return 0 if failureCount == 0 else 1
    
    except Exception as e:
        sys.stderr.write(''.join(traceback.format_exception(e)).strip())
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-include", "--protobuf-gen-base-include", type=str, required=True,
                       help="Base include path for calculating relative paths (e.g., source)")
    parser.add_argument("-asset", "--protobuf-gen-asset-folder", type=str, required=True,
                       help="Source directory containing .h files (e.g., source/Assets)")
    parser.add_argument("-proto", "--protobuf-gen-proto-folder", type=str, required=True,
                       help="Output directory for .proto files (e.g., source/ProtoGen/Protos)")
    parser.add_argument("-state", "--protobuf-gen-state-file", type=str, required=True,
                       help="Path to state file tracking modifications")
    parser.add_argument("-force", "--protobuf-gen-force-override", action="store_true",
                       help="Force regenerate all files")
    
    args = parser.parse_args()
    sys.exit(main(args))