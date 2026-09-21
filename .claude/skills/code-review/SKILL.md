---
name: code-review
description: Code review tool for analyzing code changes. Use when the user triggers with /code-review command to review uncommitted git changes or specific modules. Supports reviewing current working directory changes or targeted module analysis. Also provides post-modification code verification workflow.
watched_files:
  - scripts/get-git-diff.ps1
  - scripts/get-module-files.ps1
---

# Code Review Skill

This skill provides automated code review for git-based projects.

## 代码修改后验证流程 (Post-Modification Verification)

每次完成代码修改后，必须执行以下验证步骤：

### 步骤 1: 语法/编译检查
根据项目类型执行对应的编译检查：

**C# 项目 (Unity/.NET):**
- 使用 `dotnet build` 或 Unity 编译检查
- 检查是否有编译错误、引用错误、类型不匹配等

**其他项目类型:**
- 使用对应语言的编译器/语法检查工具

### 步骤 2: 代码审查
- 检查代码逻辑是否正确
- 检查 API 使用是否符合规范
- 检查命名规范、代码风格

### 步骤 3: 修复问题
- 如果发现错误，立即修复
- 修复后重复步骤 1-2，直到没有错误

---

**注意**: 每次修改代码后都必须执行此验证流程，确保代码质量。

## Usage

Trigger with `/code-review` command. Two modes:

### Mode 1: Review Uncommitted Changes (Default)
When user runs `/code-review` without arguments, review all uncommitted changes in the working directory.

Steps:
1. Run `scripts/get-git-diff.ps1` to get uncommitted changes
2. Analyze the diff for code quality issues
3. Provide structured review feedback

### Mode 2: Review Specific Module
When user runs `/code-review <module-name>`, review the specified module.

Steps:
1. Run `scripts/get-module-files.ps1 <module-name>` to find module files
2. Read and analyze the relevant source files
3. Provide structured review feedback

## Review Checklist

For each code review, analyze:

1. **Code Quality**
   - Variable/function naming clarity
   - Code complexity and readability
   - Proper error handling
   - Edge case handling

2. **Best Practices**
   - Language/framework conventions
   - Design patterns usage
   - DRY principle adherence
   - Single responsibility principle

3. **Potential Issues**
   - Logic errors or bugs
   - Performance concerns
   - Security vulnerabilities
   - Memory leaks

4. **Maintainability**
   - Comment quality and necessity
   - Documentation completeness
   - Test coverage indicators
   - Coupling and cohesion

## Output Format

Provide review results in this structure:

```
## 代码审查报告

### 审查范围
[描述审查的文件/模块]

### 总体评价
[简要总结代码质量]

### 详细审查结果

#### ✅ 优点
- [优点1]
- [优点2]

#### ⚠️ 建议改进
1. **[问题类别]**: [问题描述]
   - **位置**: [文件:行号]
   - **建议**: [具体改进方案]

#### 🐛 潜在问题
1. **[问题类型]**: [问题描述]
   - **位置**: [文件:行号]
   - **风险**: [可能的影响]
   - **建议**: [修复方案]

### 总结
[整体建议和行动项]
```
