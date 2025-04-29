import unittest
import os
import shutil
import tempfile
import sys
import logging

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.file_utils import create_files, create_dirs, rename_files, move_copy_files

# 设置测试日志
logging.basicConfig(level=logging.ERROR)

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, 'source')
        self.target_dir = os.path.join(self.temp_dir, 'target')
        
        # 创建源目录
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.target_dir, exist_ok=True)
        
        # 创建测试文件
        self.test_files = []
        for i in range(5):
            file_path = os.path.join(self.source_dir, f"test_file_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"测试内容 {i}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_create_files_basic(self):
        """测试基本文件创建功能"""
        file_names = ["file1", "file2", "file3"]
        result, message = create_files(
            names=file_names,
            target_dir=self.target_dir,
            file_type=".txt"
        )
        
        self.assertTrue(result)
        
        # 验证文件是否被创建
        for name in file_names:
            file_path = os.path.join(self.target_dir, name + ".txt")
            self.assertTrue(os.path.exists(file_path))
    
    def test_create_files_with_template(self):
        """测试使用模板创建文件"""
        file_names = ["file1", "file2", "file3"]
        template = "文件名: ${NAME}\n序号: ${ISEQ}"
        
        result, message = create_files(
            names=file_names,
            target_dir=self.target_dir,
            file_type=".txt",
            content_template=template,
            start_value=10,
            step=5
        )
        
        self.assertTrue(result)
        
        # 验证文件内容
        for i, name in enumerate(file_names):
            file_path = os.path.join(self.target_dir, name + ".txt")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            expected_content = template.replace("${NAME}", name)
            expected_content = expected_content.replace("${ISEQ}", str(10 + i * 5).zfill(3))
            
            self.assertEqual(content, expected_content)
    
    def test_create_files_with_naming_rule(self):
        """测试使用命名规则创建文件"""
        file_names = ["file1", "file2", "file3"]
        naming_rule = "prefix_$NAME_$ISEQ"
        
        result, message = create_files(
            names=file_names,
            target_dir=self.target_dir,
            file_type=".txt",
            naming_rule=naming_rule,
            digits=2
        )
        
        self.assertTrue(result)
        
        # 验证文件名
        for i, name in enumerate(file_names):
            expected_name = f"prefix_{name}_{str(1 + i).zfill(2)}.txt"
            file_path = os.path.join(self.target_dir, expected_name)
            self.assertTrue(os.path.exists(file_path))
    
    def test_create_dirs_basic(self):
        """测试基本目录创建功能"""
        dir_names = ["dir1", "dir2", "dir3"]
        
        result, message = create_dirs(
            names=dir_names,
            target_dir=self.target_dir
        )
        
        self.assertTrue(result)
        
        # 验证目录是否被创建
        for name in dir_names:
            dir_path = os.path.join(self.target_dir, name)
            self.assertTrue(os.path.exists(dir_path))
            self.assertTrue(os.path.isdir(dir_path))
    
    def test_create_dirs_with_hierarchy(self):
        """测试创建层级目录结构"""
        dir_names = [
            "parent1",
            "    child1_1",
            "    child1_2",
            "        grandchild1_2_1",
            "parent2",
            "    child2_1"
        ]
        
        result, message = create_dirs(
            names=dir_names,
            target_dir=self.target_dir,
            enable_hierarchy=True,
            indent_spaces=4
        )
        
        self.assertTrue(result)
        
        # 验证目录结构
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent1", "child1_1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent1", "child1_2")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent1", "child1_2", "grandchild1_2_1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent2")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "parent2", "child2_1")))
    
    def test_rename_files(self):
        """测试文件重命名"""
        # 复制测试文件到目标目录
        target_files = []
        for file_path in self.test_files:
            file_name = os.path.basename(file_path)
            target_path = os.path.join(self.target_dir, file_name)
            shutil.copy2(file_path, target_path)
            target_files.append(target_path)
        
        # 执行重命名
        success_count = rename_files(
            file_paths=target_files,
            find_text="test_file",
            replace_text="renamed_file",
            case_sensitive=True,
            whole_word=False,
            use_regex=False,
            rename_scope="both"
        )
        
        self.assertEqual(success_count, len(target_files))
        
        # 验证重命名结果
        for i in range(5):
            old_name = f"test_file_{i}.txt"
            new_name = f"renamed_file_{i}.txt"
            old_path = os.path.join(self.target_dir, old_name)
            new_path = os.path.join(self.target_dir, new_name)
            
            self.assertFalse(os.path.exists(old_path))
            self.assertTrue(os.path.exists(new_path))
    
    def test_move_copy_files(self):
        """测试移动/复制文件"""
        # 创建副本目录
        copy_dir = os.path.join(self.temp_dir, 'copy')
        os.makedirs(copy_dir, exist_ok=True)
        
        # 执行复制
        result, message = move_copy_files(
            files=self.test_files,
            target_dir=copy_dir,
            operation="copy",
            conflict_action="skip",
            preserve_structure=False
        )
        
        self.assertTrue(result)
        
        # 验证复制结果
        for i in range(5):
            file_name = f"test_file_{i}.txt"
            source_path = os.path.join(self.source_dir, file_name)
            copy_path = os.path.join(copy_dir, file_name)
            
            self.assertTrue(os.path.exists(source_path))  # 源文件仍存在
            self.assertTrue(os.path.exists(copy_path))    # 副本已创建

if __name__ == "__main__":
    unittest.main() 