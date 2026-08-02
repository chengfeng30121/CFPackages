# CFPackages
供[我自己](https://github.com/chengfeng30121)使用的实用的`Python 第三方库`! 
## 依赖
1. [colorama](https://pypi.org/project/colorama/)
2. [prompt_toolkit](https://pypi.org/project/prompt-toolkit/)
3. [questionary](https://pypi.org/project/questionary/)
4. [requests](https://pypi.org/project/requests/)
5. [pywin32](https://pypi.org/project/pywin32/) (Windows 系统下使用)
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
    export cfpackages.check_update=0
    # or
    export cfpackages.check_update=false
    ```
    或 Windows 下
    ``` cmd
    set cfpackages.check_update=0
    REM or
    set cfpackages.check_update=false
    ```
    设置 `1` 或 `true` 可强制每次导入都检查（默认 24 小时内最多检查一次，检查在后台线程进行，不会阻塞导入）。
