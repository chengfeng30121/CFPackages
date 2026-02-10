# CFPackages
供[我自己](https://github.com/chengfeng30121)使用的实用的`Python 第三方库`! 
## 依赖
1. [colorama](https://pypi.org/project/colorama/)
2. [prompt_toolkit](https://pypi.org/project/prompt-toolkit/)
3. [questions](https://pypi.org/project/questionary/)
4. [requests](https://pypi.org/project/requests/)
## 使用
1. 安装 
    ``` bash
    pip install cfpackages
    ```
2. 导入
    ``` python
    import cfpackages
    ```
3. 更新
    ``` bash
    pip install cfpackages --upgrade
    ```
4. 取消更新提示
    ``` bash
    export cfpackages.check_update=False
    # or
    export cfpackages.check_update=0
    ```
    或 Windows 下
    ``` cmd
    set cfpackages.check_update=False
    REM or
    set cfpackages.check_update=0
    ```
    或者直接打开 `cfpackages/__init__.py`, 修改脚本, 将尾部的 `if` 代码块删除.
