#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C# 自动注释添加脚本
为C#类文件添加XML注释和#region分组
"""

import re
import sys
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class MemberType(Enum):
    """成员类型枚举"""
    SERIALIZED_FIELD = auto()  # 序列化字段
    CONSTANT = auto()          # 常量
    STATIC_FIELD = auto()      # 静态字段
    FIELD = auto()             # 普通字段
    EVENT = auto()             # 事件
    PROPERTY = auto()          # 属性
    UNITY_LIFECYCLE = auto()   # Unity生命周期方法
    PUBLIC_METHOD = auto()     # 公有方法
    PROTECTED_METHOD = auto()  # 保护方法
    PRIVATE_METHOD = auto()    # 私有方法
    INTERNAL_METHOD = auto()   # 内部方法
    CONSTRUCTOR = auto()       # 构造函数


@dataclass
class MemberInfo:
    """成员信息"""
    name: str
    member_type: MemberType
    return_type: str = ""
    parameters: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    is_static: bool = False
    is_override: bool = False
    is_async: bool = False
    original_text: str = ""
    start_line: int = 0
    end_line: int = 0
    existing_comment: str = ""


class CSharpCommentAdder:
    """C#注释添加器"""
    
    # Unity生命周期方法名
    UNITY_LIFECYCLE_METHODS = {
        'Awake', 'Start', 'OnEnable', 'OnDisable', 'OnDestroy',
        'Update', 'FixedUpdate', 'LateUpdate',
        'OnTriggerEnter', 'OnTriggerExit', 'OnTriggerStay',
        'OnCollisionEnter', 'OnCollisionExit', 'OnCollisionStay',
        'OnMouseDown', 'OnMouseUp', 'OnMouseEnter', 'OnMouseExit',
        'OnValidate', 'Reset', 'OnDrawGizmos', 'OnGUI',
        'OnApplicationPause', 'OnApplicationQuit', 'OnApplicationFocus'
    }
    
    # 区域显示名称映射
    REGION_NAMES = {
        MemberType.SERIALIZED_FIELD: "Serialized Fields",
        MemberType.CONSTANT: "Constants",
        MemberType.STATIC_FIELD: "Static Fields",
        MemberType.FIELD: "Fields",
        MemberType.EVENT: "Events",
        MemberType.PROPERTY: "Properties",
        MemberType.UNITY_LIFECYCLE: "Unity Lifecycle",
        MemberType.PUBLIC_METHOD: "Public Methods",
        MemberType.PROTECTED_METHOD: "Protected Methods",
        MemberType.PRIVATE_METHOD: "Private Methods",
        MemberType.INTERNAL_METHOD: "Internal Methods",
        MemberType.CONSTRUCTOR: "Constructors",
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.lines: List[str] = []
        self.members: List[MemberInfo] = []
        self.class_start_line = 0
        self.class_end_line = 0
        
    def load_file(self) -> bool:
        """加载C#文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.split('\n')
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def parse(self):
        """解析C#文件，提取成员信息"""
        in_multiline_comment = False
        in_string = False
        string_char = None
        brace_depth = 0
        class_depth = 0
        current_member_lines = []
        current_member_start = 0
        current_attributes = []
        
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                continue
            
            # 处理多行注释
            if '/*' in stripped and not in_multiline_comment:
                if '*/' not in stripped:
                    in_multiline_comment = True
                continue
            
            if in_multiline_comment:
                if '*/' in stripped:
                    in_multiline_comment = False
                continue
            
            # 处理单行注释
            if stripped.startswith('//'):
                continue
            
            # 追踪大括号深度
            for char in stripped:
                if char in '"\'':
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif string_char == char:
                        in_string = False
                        string_char = None
            
            # 统计大括号
            if not in_string:
                brace_depth += stripped.count('{') - stripped.count('}')
            
            # 检测类定义开始
            if re.match(r'\s*(public|private|protected|internal|abstract|sealed|static|partial)*\s*class\s+\w+', stripped):
                if brace_depth == 1:  # 类内部深度为1
                    class_depth = brace_depth
                    self.class_start_line = i
                    continue
            
            # 检测特性
            if stripped.startswith('[') and stripped.endswith(']'):
                current_attributes.append(stripped)
                continue
            
            # 检测成员
            member_info = self._detect_member(stripped, current_attributes, i)
            if member_info:
                member_info.original_text = line
                member_info.start_line = i
                self.members.append(member_info)
                current_attributes = []
            
            # 检测现有XML注释
            if stripped.startswith('///'):
                continue
        
        # 查找类结束行
        if self.class_start_line > 0:
            temp_depth = 0
            for i in range(self.class_start_line, len(self.lines)):
                temp_depth += self.lines[i].count('{') - self.lines[i].count('}')
                if temp_depth == 0:
                    self.class_end_line = i
                    break
    
    def _detect_member(self, line: str, attributes: List[str], line_num: int) -> Optional[MemberInfo]:
        """检测并解析成员"""
        
        # 跳过using、namespace等
        if line.startswith('using ') or line.startswith('namespace '):
            return None
        
        # 匹配字段 (支持特性)
        field_match = re.match(
            r'\s*((?:\[\w+\]\s*)*)\s*(public|private|protected|internal)?\s*(static|readonly|const)?\s*(\w+)\s+(\w+)\s*(?:=\s*.+)?;',
            line
        )
        if field_match:
            attrs_str = field_match.group(1) or ""
            attrs = re.findall(r'\[(\w+)\]', attrs_str)
            modifiers = [m for m in [field_match.group(2), field_match.group(3)] if m]
            return self._create_field_info(field_match.group(5), field_match.group(4), 
                                          modifiers, attrs, line_num)
        
        # 匹配属性
        prop_match = re.match(
            r'\s*(public|private|protected|internal)?\s*(static|virtual|abstract|override|sealed)?\s*(\w+)\s+(\w+)\s*\{',
            line
        )
        if prop_match:
            modifiers = [m for m in [prop_match.group(1), prop_match.group(2)] if m]
            return self._create_property_info(prop_match.group(4), modifiers, line_num)
        
        # 匹配方法 (包含async)
        method_match = re.match(
            r'\s*(public|private|protected|internal)?\s*(static|virtual|abstract|override|sealed|async|abstract|extern)?\s*(async\s+)?(\w+)\s+(\w+)\s*\((.*?)\)',
            line
        )
        if method_match:
            access = method_match.group(1) or 'private'
            modifier = method_match.group(2) or ''
            is_async = method_match.group(3) is not None or 'async' in modifier
            return_type = method_match.group(4)
            name = method_match.group(5)
            params = method_match.group(6)
            
            modifiers = [m for m in [access, modifier.replace('async', '').strip()] if m]
            
            return self._create_method_info(name, return_type, params, modifiers, 
                                          is_async, 'override' in modifier, line_num)
        
        # 匹配事件
        event_match = re.match(
            r'\s*(public|private|protected|internal)?\s*(static)?\s*event\s+(\w+)\s+(\w+)',
            line
        )
        if event_match:
            access = event_match.group(1) or 'private'
            modifiers = [access]
            if event_match.group(2):
                modifiers.append(event_match.group(2))
            return MemberInfo(
                name=event_match.group(4),
                member_type=MemberType.EVENT,
                return_type=event_match.group(3),
                modifiers=modifiers,
                start_line=line_num
            )
        
        return None
    
    def _create_field_info(self, name: str, field_type: str, modifiers: List[str], 
                          attributes: List[str], line_num: int) -> MemberInfo:
        """创建字段信息"""
        member_type = MemberType.FIELD
        
        if 'const' in modifiers:
            member_type = MemberType.CONSTANT
        elif 'static' in modifiers:
            member_type = MemberType.STATIC_FIELD
        elif 'SerializeField' in attributes or any('SerializeField' in attr for attr in attributes):
            member_type = MemberType.SERIALIZED_FIELD
        
        return MemberInfo(
            name=name,
            member_type=member_type,
            return_type=field_type,
            modifiers=modifiers,
            attributes=attributes,
            start_line=line_num
        )
    
    def _create_property_info(self, name: str, modifiers: List[str], line_num: int) -> MemberInfo:
        """创建属性信息"""
        return MemberInfo(
            name=name,
            member_type=MemberType.PROPERTY,
            modifiers=modifiers,
            start_line=line_num
        )
    
    def _create_method_info(self, name: str, return_type: str, params: str, 
                           modifiers: List[str], is_async: bool, is_override: bool,
                           line_num: int) -> MemberInfo:
        """创建方法信息"""
        # 确定方法类型
        member_type = MemberType.PRIVATE_METHOD
        
        access = next((m for m in modifiers if m in ['public', 'private', 'protected', 'internal']), 'private')
        
        if name in self.UNITY_LIFECYCLE_METHODS:
            member_type = MemberType.UNITY_LIFECYCLE
        elif name == self._get_class_name():
            member_type = MemberType.CONSTRUCTOR
        elif access == 'public':
            member_type = MemberType.PUBLIC_METHOD
        elif access == 'protected':
            member_type = MemberType.PROTECTED_METHOD
        elif access == 'internal':
            member_type = MemberType.INTERNAL_METHOD
        
        # 解析参数
        param_list = []
        if params.strip():
            for p in params.split(','):
                p = p.strip()
                if p:
                    parts = p.split()
                    if len(parts) >= 2:
                        param_list.append(parts[-1])  # 参数名
        
        return MemberInfo(
            name=name,
            member_type=member_type,
            return_type=return_type,
            parameters=param_list,
            modifiers=modifiers,
            is_async=is_async,
            is_override=is_override,
            start_line=line_num
        )
    
    def _get_class_name(self) -> str:
        """从文件内容提取类名"""
        match = re.search(r'class\s+(\w+)', self.content)
        return match.group(1) if match else ""
    
    def _generate_comment(self, member: MemberInfo) -> str:
        """生成XML注释"""
        lines = []
        
        if member.member_type == MemberType.METHOD or member.member_type in [
            MemberType.UNITY_LIFECYCLE, MemberType.PUBLIC_METHOD,
            MemberType.PROTECTED_METHOD, MemberType.PRIVATE_METHOD,
            MemberType.INTERNAL_METHOD, MemberType.CONSTRUCTOR
        ]:
            # 方法注释
            async_prefix = "异步" if member.is_async else ""
            override_prefix = "重写" if member.is_override else ""
            
            summary = f"{async_prefix}{override_prefix}方法功能简述".strip()
            if member.member_type == MemberType.CONSTRUCTOR:
                summary = "构造函数"
            elif member.name in self.UNITY_LIFECYCLE_METHODS:
                summary = self._get_lifecycle_description(member.name)
            
            lines.append(f"/// <summary>")
            lines.append(f"/// {summary}")
            lines.append(f"/// </summary>")
            
            # 参数
            for param in member.parameters:
                lines.append(f"/// <param name=\"{param}\">参数说明</param>")
            
            # 返回值
            if member.return_type and member.return_type != 'void':
                lines.append(f"/// <returns>返回值说明</returns>")
        
        elif member.member_type == MemberType.PROPERTY:
            lines.append(f"/// <summary>")
            lines.append(f"/// {member.name} 属性")
            lines.append(f"/// </summary>")
        
        elif member.member_type in [MemberType.FIELD, MemberType.SERIALIZED_FIELD, 
                                   MemberType.STATIC_FIELD, MemberType.CONSTANT]:
            lines.append(f"/// <summary>")
            lines.append(f"/// {member.name} 字段")
            lines.append(f"/// </summary>")
        
        elif member.member_type == MemberType.EVENT:
            lines.append(f"/// <summary>")
            lines.append(f"/// {member.name} 事件")
            lines.append(f"/// </summary>")
        
        return '\n'.join(lines)
    
    def _get_lifecycle_description(self, method_name: str) -> str:
        """获取Unity生命周期方法描述"""
        descriptions = {
            'Awake': "当脚本实例被加载时调用",
            'Start': "在第一帧更新之前调用",
            'OnEnable': "当对象变为启用和激活状态时调用",
            'OnDisable': "当对象变为禁用或非激活状态时调用",
            'OnDestroy': "当对象将被销毁时调用",
            'Update': "每帧调用一次",
            'FixedUpdate': "固定时间间隔调用，用于物理更新",
            'LateUpdate': "每帧在所有Update调用后调用",
        }
        return descriptions.get(method_name, f"{method_name} 生命周期方法")
    
    def _has_existing_comment(self, line_idx: int) -> bool:
        """检查成员前是否已有XML注释"""
        if line_idx <= 0:
            return False
        
        # 向上查找连续的三斜杠注释
        i = line_idx - 1
        while i >= 0:
            line = self.lines[i].strip()
            if line.startswith('///'):
                return True
            elif line and not line.startswith('[') and not line.startswith('//'):
                # 遇到了非注释、非空行、非特性行
                break
            i -= 1
        return False
    
    def _organize_with_regions(self) -> str:
        """使用#region重新组织代码"""
        # 按类型分组成员
        grouped: Dict[MemberType, List[MemberInfo]] = {t: [] for t in MemberType}
        for member in self.members:
            grouped[member.member_type].append(member)
        
        # 确定类型顺序
        type_order = [
            MemberType.CONSTANT,
            MemberType.SERIALIZED_FIELD,
            MemberType.STATIC_FIELD,
            MemberType.FIELD,
            MemberType.EVENT,
            MemberType.PROPERTY,
            MemberType.CONSTRUCTOR,
            MemberType.UNITY_LIFECYCLE,
            MemberType.PUBLIC_METHOD,
            MemberType.PROTECTED_METHOD,
            MemberType.INTERNAL_METHOD,
            MemberType.PRIVATE_METHOD,
        ]
        
        # 构建输出
        result_lines = []
        
        # 添加文件头（using、namespace等）
        for i in range(self.class_start_line + 1):
            result_lines.append(self.lines[i])
        
        # 按组添加成员
        first_region = True
        for member_type in type_order:
            members = grouped[member_type]
            if not members:
                continue
            
            if not first_region:
                result_lines.append("")
            first_region = False
            
            region_name = self.REGION_NAMES.get(member_type, str(member_type))
            result_lines.append(f"\n    #region {region_name}")
            result_lines.append("")
            
            for member in members:
                # 添加注释
                if not self._has_existing_comment(member.start_line):
                    comment = self._generate_comment(member)
                    for comment_line in comment.split('\n'):
                        result_lines.append(f"    {comment_line}")
                
                # 添加成员代码
                result_lines.append(self.lines[member.start_line])
            
            result_lines.append("")
            result_lines.append(f"    #endregion // {region_name}")
        
        # 添加类结束和文件尾部
        for i in range(self.class_end_line, len(self.lines)):
            result_lines.append(self.lines[i])
        
        return '\n'.join(result_lines)
    
    def process(self) -> str:
        """处理文件并返回结果"""
        if not self.load_file():
            return ""
        
        self.parse()
        
        if not self.members:
            print("No members found to process.")
            return self.content
        
        return self._organize_with_regions()
    
    def save(self, output_path: Optional[str] = None):
        """保存处理后的文件"""
        result = self.process()
        if not result:
            return False
        
        path = output_path or self.file_path
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Processed file saved to: {path}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_comments.py <csharp_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        sys.exit(1)
    
    adder = CSharpCommentAdder(file_path)
    adder.save()


if __name__ == "__main__":
    main()
